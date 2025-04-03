from flask import Flask, request, jsonify
import pika
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import threading
import time  # Add this with other imports
import os

QUEUE_NAME = "notification_queue"

# Mailgun SMTP Settings
SMTP_SERVER = os.getenv('SMTP_SERVER', 'default_smtp_server')  # Default to blank or strong if not set
SMTP_PORT = os.getenv('SMTP_PORT', 587)  # Default to 587 if not set
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')  # Default to blank if not set
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')  # Default to blank if not set
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')  # Default to blank if not set
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')  # Default to blank if not set

app = Flask(__name__)

# To accumulate alerts
alert_batch = []

# To accumulate notification of supplier orders
order_batch = []

def send_email(alerts):
    try:
        # Setup MIME
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = 'Low Rating Alerts'

        # Construct email body
        body = "The following products have received bad reviews:\n\n"
        for alert in alerts:
            body += f"- {alert['menu_item_id']} (Rating: {alert['average_rating']}/5)\n"

        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)  # Login using your SMTP username and password
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

        print(f"Email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_email_order(body_order):
    try:
        # Setup MIME
        msg_order = MIMEMultipart()
        msg_order['From'] = SENDER_EMAIL
        msg_order['To'] = RECIPIENT_EMAIL
        msg_order['Subject'] = "MEALSGO - Weekly Ingredient Orders Status"

        # Attach the formatted email body
        msg_order.attach(MIMEText(body_order, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg_order.as_string())

        print(f"Order status email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending order email: {e}")
        
# AMQP Consumer to get messages from the queue
def callback(ch, method, properties, body):
    try:
        alert_msg = json.loads(body)
        print(f"Received alert: {alert_msg}")

        # Add the alert to the batch
        alert_batch.append(alert_msg)

        # If the batch has 2 or more alerts, send them in one email
        if len(alert_batch) >= 2:
            send_email(alert_batch)
            alert_batch.clear()  # Clear the batch after sending the email

        # Acknowledge that the message has been processed
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")

def process_notification_order(ch, method, properties, body_order):
    try:
        notification_data = json.loads(body_order)
        order_batch.append(notification_data)

        print(order_batch)
        # Early exit if not enough orders
        if len(order_batch) < 3:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Separate successful and failed orders
        success_orders = []
        failed_orders = []
        
        for order in order_batch:
            if order.get("status") == "error":
                failed_orders.append(order)
            else:
                success_orders.append(order)

        # Build email content
        body_order = ""

        # Add successful orders section
        if success_orders:
            body_order += "Status: Success\n"
            body_order += "================\n"
            for order in success_orders:
                body_order += f"Message: {order.get('message', 'No details')}\n"
                body_order += f"Supplier: {order.get('supplier', 'N/A')}\n"
                body_order += f"Ingredient: {order.get('ingredient', 'N/A')}\n"
                body_order += f"Trace ID: {order.get('trace_id', 'N/A')}\n"
                body_order += "----------------\n"
            body_order += "\n"

        # Add failed orders section
        if failed_orders:
            body_order += "Status: Failure\n"
            body_order += "================\n"
            for order in failed_orders:
                body_order += f"Error: {order.get('message', 'No details')}\n"
                body_order += f"Supplier: {order.get('supplier', 'N/A')}\n"
                body_order += f"Ingredient: {order.get('ingredient', 'N/A')}\n"
                body_order += f"Trace ID: {order.get('trace_id', 'N/A')}\n"
                body_order += "----------------\n"
            body_order += "\n"


            # Add summary
            body_order += f"Summary - Success: {len(success_orders)}, Failed: {len(failed_orders)}"

        # Send the email
        send_email_order(body_order)
        order_batch.clear()  # Clear the batch after sending

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Error processing order notification: {str(e)}")

# Setup RabbitMQ connection
def listen_to_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))  
    channel = connection.channel()

    # Declare the queue to ensure it exists
    channel.queue_declare(queue='feedback_alert', durable=True)

    # Set up the consumer
    channel.basic_consume(queue='feedback_alert', on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

def start_amqp_consumer():
    purged = False  # Track if purge happened
    # print(purged)
    while True:  # Retry loop for connection
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="host.docker.internal"))
            channel = connection.channel()
            
            if not purged:
                channel.queue_purge(queue=QUEUE_NAME)
                purged = True  # Mark as done
                print(f" [*] Purged all messages from {QUEUE_NAME}")
                # print(purged)
            # Start consuming new messages
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_notification_order)
            print(" [*] Waiting for new messages. To exit press CTRL+C")
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError:
            print(" [X] Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    # listen_to_queue()
    threading.Thread(target=listen_to_queue, daemon=True).start() #see if this works
    # Start RabbitMQ consumer in a separate thread
    threading.Thread(target=start_amqp_consumer, daemon=True).start()
    app.run(host='0.0.0.0', port=5021)