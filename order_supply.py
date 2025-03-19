from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import json
from os import environ
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# AMQP configuration
RABBITMQ_HOST = environ.get("RABBITMQ_HOST") or "localhost"
QUEUE_FROM_RESTOCKING = "order_supply_queue"  # Queue to receive orders from Restocking Service
QUEUE_TO_RESTOCKING = "restocking_response_queue"  # Queue to send responses back to Restocking Service
QUEUE_TO_NOTIFICATION = "notification_queue"  # Queue to send notifications
QUEUE_TO_NEXT_SUPPLIER = "next_supplier_queue"  # Queue to request the next preferred supplier

def send_to_queue(queue_name, message):
    """Send a message to a specified queue via AMQP."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(message))
    connection.close()
    print(f" [Order Supply Service] Sent to {queue_name}: {message}")

def simulate_external_supplier(order_data):
    """Simulate ordering from an external supplier and return a response."""
    print(f" [Order Supply Service] Simulating order from external supplier: {order_data}")
    time.sleep(2)  # Simulate a delay in processing

    ingredient_name = order_data["ingredient_name"]
    supplier_name = order_data["supplier_name"]

    # Simulate success/failure based on supplier and ingredient
    if ingredient_name == "Tomato":
        if supplier_name == "Fresh Farms":  # Priority 1
            return {
                "status": "error",
                "message": f"Failed to place order with {supplier_name}.",
                "order_data": order_data
            }
        elif supplier_name == "Organic Goods":  # Priority 2
            return {
                "status": "success",
                "message": f"Order for {order_data['amount_needed']} units of {ingredient_name} placed successfully with {supplier_name}.",
                "order_data": order_data
            }
    elif ingredient_name == "Cheese":
        if supplier_name == "Dairy Delight":  # Priority 1
            return {
                "status": "error",
                "message": f"Failed to place order with {supplier_name}.",
                "order_data": order_data
            }
    elif ingredient_name == "Lettuce":
        if supplier_name == "Fresh Farms":  # Priority 1
            return {
                "status": "success",
                "message": f"Order for {order_data['amount_needed']} units of {ingredient_name} placed successfully with {supplier_name}.",
                "order_data": order_data
            }

# def process_order_request(order_data, retry_count=0):
#     """Process an order request by simulating an external supplier and handling success/failure."""
#     try:
#         # Simulate ordering from the supplier
#         supplier_response = simulate_external_supplier(order_data)

#         if supplier_response["status"] == "success":
#             # 5a) If the order succeeds, send a success message to the Notification Service
#             notification_message = {
#                 "type": "order_success",
#                 "message": supplier_response["message"],
#                 "order_data": supplier_response["order_data"]
#             }
#             send_to_queue(QUEUE_TO_NOTIFICATION, notification_message)
#             print(f" [Order Supply Service] Order succeeded. Notification sent: {notification_message}")
#         else:
#             # 5b) If the order fails, request the next preferred supplier
#             next_supplier_request = {
#                 "ingredient_name": order_data["ingredient_name"],
#                 "amount_needed": order_data["amount_needed"],
#                 "unit_of_measure": order_data["unit_of_measure"],
#                 "retry_count": retry_count + 1
#             }
#             send_to_queue(QUEUE_TO_NEXT_SUPPLIER, next_supplier_request)
#             print(f" [Order Supply Service] Order failed. Requesting next supplier: {next_supplier_request}")
#     except Exception as e:
#         print(f" [Order Supply Service] Error processing order: {e}")
#         error_message = {
#             "type": "error",
#             "message": f"Internal error processing order: {str(e)}",
#             "order_data": order_data
#         }
#         send_to_queue(QUEUE_TO_NOTIFICATION, error_message)

def process_order_request(order_data, retry_count=0):
    """Process an order request by simulating an external supplier and handling success/failure."""
    try:
        # Check if the message is an error
        if "type" in order_data and order_data["type"] == "error":
            # Forward the error to the Notification Service
            error_message = {
                "type": "error",
                "message": order_data["message"],
                "order_data": order_data.get("order_data", {})
            }
            send_to_queue(QUEUE_TO_NOTIFICATION, error_message)
            print(f" [Order Supply Service] Error forwarded to Notification Service: {error_message}")
            return

        # Simulate ordering from the supplier
        supplier_response = simulate_external_supplier(order_data)

        if supplier_response["status"] == "success":
            # 5a) If the order succeeds, send a success message to the Notification Service
            notification_message = {
                "type": "order_success",
                "message": supplier_response["message"],
                "order_data": supplier_response["order_data"]
            }
            send_to_queue(QUEUE_TO_NOTIFICATION, notification_message)
            print(f" [Order Supply Service] Order succeeded. Notification sent: {notification_message}")
        else:
            # 5b) If the order fails, request the next preferred supplier
            next_supplier_request = {
                "ingredient_name": order_data["ingredient_name"],
                "amount_needed": order_data["amount_needed"],
                "unit_of_measure": order_data["unit_of_measure"],
                "retry_count": retry_count + 1
            }
            send_to_queue(QUEUE_TO_NEXT_SUPPLIER, next_supplier_request)
            print(f" [Order Supply Service] Order failed. Requesting next supplier: {next_supplier_request}")
    except Exception as e:
        print(f" [Order Supply Service] Error processing order: {e}")
        error_message = {
            "type": "error",
            "message": f"Internal error processing order: {str(e)}",
            "order_data": order_data
        }
        send_to_queue(QUEUE_TO_NOTIFICATION, error_message)

def start_amqp_consumer():
    """Start consuming messages from the Restocking Service's AMQP queue."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_FROM_RESTOCKING)

    def callback(ch, method, properties, body):
        try:
            order_data = json.loads(body)
            print(f" [Order Supply Service] Received order request: {order_data}")
            process_order_request(order_data)
        except Exception as e:
            print(f" [Order Supply Service] Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_FROM_RESTOCKING, on_message_callback=callback)
    print(" [Order Supply Service] Waiting for order requests...")
    channel.start_consuming()

if __name__ == "__main__":
    # Start the AMQP consumer in a separate thread
    amqp_thread = threading.Thread(target=start_amqp_consumer)
    amqp_thread.daemon = True
    amqp_thread.start()

    # Start the Flask app
    app.run(host="0.0.0.0", port=5006, debug=True)