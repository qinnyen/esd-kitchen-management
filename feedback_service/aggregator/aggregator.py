# This script is meant to be scheduled once a week

from feedback_service.feedback import db, Feedback, app  # Reuse existing model and DB config
from sqlalchemy import func
import pika
import json
import os

# Configuration for RabbitMQ connection
RABBITMQ_HOST = "rabbitmq"  
QUEUE_NAME = "feedback_alert" #name of the queue

# Create the application context so SQLAlchemy works outside Flask route
with app.app_context():
    # Step 1: Query average rating per menu_item_id
    avg_ratings = db.session.query(
        Feedback.menu_item_id,
        func.avg(Feedback.rating).label("avg_rating") #rename the result to "avg_rating" in the query output
    ).group_by(Feedback.menu_item_id).all()

    # Step 2: Filter menu items with average rating ≤ 2
    low_rating_items = [item for item in avg_ratings if item.avg_rating <= 2]

    if not low_rating_items:
        print("No low-rated menu items found this week.")
    else:
        print(f"Found {len(low_rating_items)} low-rated item(s). Sending alert...")

        # Step 3: Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel() #create channel

        # Declare the queue (idempotent) create queue if it does not exists
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        # Step 4: Publish each low-rated item to the queue
        for item in low_rating_items:
            alert_msg = {
                "menu_item_id": item[0],  # Access the menu_item_id correctly
                "average_rating": round(float(item[1]), 2),  # Access the avg_rating correctly and round it
                "message": "Average weekly rating below threshold"
            }

            # Send the message
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(alert_msg),
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
            )

            print(f"Alert sent for item: {item.menu_item_id}")

        # Clean up connection
        connection.close()
