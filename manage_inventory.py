from flask import Flask
import pika
import json
import threading
import requests
import uuid

app = Flask(__name__)

RABBITMQ_HOST = "localhost"
QUEUE_FROM_RESTOCKING = "manage_inventory_queue"
QUEUE_TO_NOTIFICATION = "notification_queue"
API_GATEWAY_URL = "http://localhost:5007"

def send_to_queue(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(message))
    connection.close()
    print(f" [Order Supply] Sent to {queue_name}: {message}")

def process_order_request(ch, method, properties, body):
    order_data = json.loads(body)
    trace_id = str(uuid.uuid4())
    
    try:
        # Step 1: Check availability with pre-filtered suppliers
        availability_response = requests.post(
            f"{API_GATEWAY_URL}/check_availability",
            json={
                "ingredient_name": order_data["ingredient_name"],
                "suppliers": order_data["suppliers"]
            },
            timeout=5
        ).json()
        
        available_suppliers = availability_response.get("available_suppliers", [])
        
        if not available_suppliers:
            raise Exception(f"No available suppliers for {order_data['ingredient_name']}")
        
        # Step 2: Place order with first available supplier
        order_result = requests.post(
            f"{API_GATEWAY_URL}/place_order",
            json={
                "ingredient_name": order_data["ingredient_name"],
                "supplier_name": available_suppliers[0],
                "amount": order_data["amount_needed"],
                "unit": order_data["unit_of_measure"]
            },
            timeout=5  # Reduced timeout
        ).json()
        
        # Add trace ID to success responses
        order_result["trace_id"] = trace_id
        send_to_queue(QUEUE_TO_NOTIFICATION, order_result)
        
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