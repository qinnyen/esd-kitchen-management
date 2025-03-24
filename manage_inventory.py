from flask import Flask
import pika
import json
import threading
import requests

app = Flask(__name__)

RABBITMQ_HOST = "localhost"
QUEUE_FROM_RESTOCKING = "manage_inventory_queue"
QUEUE_TO_NOTIFICATION = "notification_queue"
SUPPLIER_PLATFORM_URL = "http://localhost:5007/place_order"

def send_to_queue(queue_name, message):
    """Send a message to a specified queue via AMQP."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(message))
    connection.close()
    print(f" [Order Supply Service] Sent to {queue_name}: {message}")

def process_order_request(ch, method, properties, body):
    order_data = json.loads(body)
    try:
        suppliers = [{"name": name} for name in order_data["suppliers"]]
        
        response = requests.post(
            SUPPLIER_PLATFORM_URL,
            json={
                "ingredient_name": order_data["ingredient_name"],
                "amount_needed": order_data["amount_needed"],
                "unit_of_measure": order_data["unit_of_measure"],
                "suppliers": suppliers  
            },
            timeout=5
        )
        send_to_queue(QUEUE_TO_NOTIFICATION, response.json())
    except Exception as e:
        send_to_queue(QUEUE_TO_NOTIFICATION, {
            "type": "error",
            "message": f"Order failed: {str(e)}"
        })
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_amqp_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_FROM_RESTOCKING)
    channel.basic_consume(
        queue=QUEUE_FROM_RESTOCKING,
        on_message_callback=process_order_request
    )
    channel.start_consuming()

if __name__ == "__main__":
    threading.Thread(target=start_amqp_consumer, daemon=True).start()
    app.run(host="0.0.0.0", port=5006, debug=False)