#this is the code for smtp server

from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import os
from dotenv import load_dotenv
import pika
import json
import threading
import time  # Add this with other imports

# Load environment variables
load_dotenv()

app = Flask(__name__)

# RabbitMQ Configuration
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "notification_queue"

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("GMAIL_ADDRESS")  # Load from .env
SMTP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Load from .env
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")  # Load from .env

def send_email(to_email, subject, body):
    """Send email using Gmail SMTP"""
    try:
        # Create message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = formataddr(("MEALSGO", SMTP_USERNAME))
        msg['To'] = to_email

        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def process_notification(ch, method, properties, body):
    try:
        notification_data = json.loads(body)
        print(f" [Notification Service] Received: {notification_data}")
        
        # Determine email content based on notification type
        if notification_data.get("status") == "error":
            subject = "MEALSGO - Order Error Notification"
            body = f"""
            Error in inventory order:
            
            Message: {notification_data.get("message", "No details provided")}
            Trace ID: {notification_data.get("trace_id", "N/A")}
            Ingredient: {notification_data.get("ingredient", "Unknown")}
            Amount: {notification_data.get("requested_amount", "N/A")} {notification_data.get("requested_unit", "")}
            
            Please check the system for details.
            """
        else:
            subject = "MEALSGO - Order Success Notification"
            body = f"""
            Successful order placed:
            
            Message: {notification_data.get("message")}
            Supplier: {notification_data.get("supplier")}            
            Trace ID: {notification_data.get("trace_id", "N/A")}
            
            The order has been successfully processed.
            """
        
        # Send to admin email (you might want to make this configurable)
        admin_email = os.getenv(ADMIN_EMAIL, SMTP_USERNAME)
        send_email(admin_email, subject, body)
        
    except Exception as e:
        print(f" [X] Error processing notification: {str(e)}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_amqp_consumer():
    purged = False  # Track if purge happened
    # print(purged)
    while True:  # Retry loop for connection
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            channel = connection.channel()
            
            if not purged:
                channel.queue_purge(queue=QUEUE_NAME)
                purged = True  # Mark as done
                print(f" [*] Purged all messages from {QUEUE_NAME}")
                # print(purged)
            # Start consuming new messages
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_notification)
            print(" [*] Waiting for new messages. To exit press CTRL+C")
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError:
            print(" [X] Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            break
# def start_amqp_consumer():
#     connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
#     channel = connection.channel()
#     channel.queue_declare(queue=QUEUE_NAME)
#     channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_notification)
#     print(" [*] Notification service waiting for messages. To exit press CTRL+C")
#     channel.start_consuming()

@app.route('/send-notification', methods=['POST'])
def handle_send_email():
    """API endpoint to send emails"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['to', 'subject', 'body']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Send email
    success = send_email(
        to_email=data['to'],
        subject=data['subject'],
        body=data['body']
    )
    
    if success:
        return jsonify({"message": "Email sent successfully!"}), 200
    else:
        return jsonify({"error": "Failed to send email."}), 500

if __name__ == '__main__':
    # Start RabbitMQ consumer in a separate thread
    threading.Thread(target=start_amqp_consumer, daemon=True).start()
    app.run(host='0.0.0.0', port=5020)
