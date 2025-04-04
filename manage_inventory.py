from flask import Flask
import pika
import json
import threading
import requests
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

RABBITMQ_HOST = "localhost"
QUEUE_FROM_RESTOCKING = "manage_inventory_queue"
QUEUE_TO_NOTIFICATION = "notification_queue"

# Supplier URLs (moved from api_gateway.py)
SUPPLIER_URLS = {
    "Cheese Haven": "http://localhost:5016",
    "Organic Goods": "http://localhost:5011",
    "Dairy Delight": "http://localhost:5012",
    "Lettuce Land": "http://localhost:5017",
    "Fresh Farms": "http://localhost:5010",
    "Tomato Express": "http://localhost:5018"
}

def send_to_queue(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(message))
    connection.close()
    print(f" [Order Supply] Sent to {queue_name}: {message}")

def check_availability(ingredient_name, suppliers):
    """Replicates the exact JSON structure of the original API Gateway."""
    available_suppliers = []
    with ThreadPoolExecutor() as executor:
        future_to_supplier = {
            executor.submit(
                requests.get,
                f"{SUPPLIER_URLS[supplier]}/check_availability",
                params={"ingredient_name": ingredient_name},
                timeout=5
            ): supplier for supplier in suppliers
        }
        for future in as_completed(future_to_supplier, timeout=5):
            supplier = future_to_supplier[future]
            try:
                if future.result().json().get("available"):
                    available_suppliers.append(supplier)
            except:
                continue
    
    # Match the original API Gateway's JSON structure
    return {
        "available_suppliers": available_suppliers,
        "ingredient": ingredient_name  # Include for backward compatibility
    }

def place_order(supplier_name, order_data):
    try:
        response = requests.post(
            f"{SUPPLIER_URLS[supplier_name]}/place_order",
            json=order_data,
            timeout=5
        )
        result = response.json()
        result["gateway_status"] = "processed"  # Additional metadata
        return result
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "supplier": supplier_name,
            "ingredient": order_data.get("ingredient_name"),
            "message": "Supplier timeout"
        }
    except Exception as e:
        return {
            "status": "error",
            "supplier": supplier_name,
            "ingredient": order_data.get("ingredient_name"),
            "message": f"Gateway error: {str(e)}"
        }

def process_order_request(ch, method, properties, body):
    order_data = json.loads(body)
    trace_id = str(uuid.uuid4())
    
    try:
        availability_response = check_availability(
            ingredient_name=order_data["ingredient_name"],
            suppliers=order_data["suppliers"]
        )
        available_suppliers = availability_response["available_suppliers"]
        
        if not available_suppliers:
            raise Exception(f"No suppliers available for {order_data['amount_needed']}{order_data['unit_of_measure']} of {order_data['ingredient_name']}")
        
        # Try suppliers until one succeeds
        for supplier in available_suppliers:
            try:
                order_result = place_order(
                    supplier_name=supplier,
                    order_data={
                        "ingredient_name": order_data["ingredient_name"],
                        "amount": order_data["amount_needed"],
                        "unit": order_data["unit_of_measure"]
                    }
                )
                if order_result.get("status") != "error":
                    order_result["trace_id"] = trace_id
                    send_to_queue(QUEUE_TO_NOTIFICATION, order_result)
                    return
            except Exception:
                continue
        
        raise Exception(f"All suppliers failed for {order_data['ingredient_name']}")
    
    except Exception as e:
        send_to_queue(QUEUE_TO_NOTIFICATION, {
            "status": "error",
            "message": str(e),  
            "trace_id": trace_id,
            "ingredient": order_data["ingredient_name"],
            "requested_amount": order_data["amount_needed"],
            "requested_unit": order_data["unit_of_measure"]
        })
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_amqp_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_FROM_RESTOCKING)
    channel.basic_consume(queue=QUEUE_FROM_RESTOCKING, on_message_callback=process_order_request)
    print(" [*] Waiting for restocking requests. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    threading.Thread(target=start_amqp_consumer, daemon=True).start()
    app.run(host="0.0.0.0", port=5006, debug=False)