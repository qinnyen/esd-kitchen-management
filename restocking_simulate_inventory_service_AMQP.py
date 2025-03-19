# simulate_inventory_service.py
import pika
import json

# AMQP configuration
RABBITMQ_HOST = "localhost"
QUEUE_TO_RESTOCKING = "restocking_queue"

# Create a connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Declare the queue (in case it doesn't exist)
channel.queue_declare(queue=QUEUE_TO_RESTOCKING)

# Simulate a restock request
restock_request = {
    "ingredient_name": "Tomato",
    "amount_needed": 100
}

# Publish the message to the queue
channel.basic_publish(
    exchange="",
    routing_key=QUEUE_TO_RESTOCKING,
    body=json.dumps(restock_request)
)

print(f" [Inventory Service] Sent restock request: {restock_request}")
connection.close()