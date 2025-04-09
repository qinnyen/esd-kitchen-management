from flask import Flask
import pika
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import threading
import time
import os
from queue import Queue  # Thread-safe queue for orders

# --- Constants and Config ---
QUEUE_NAME = "notification_queue"
SMTP_SERVER = os.getenv('SMTP_SERVER', 'default_smtp_server')
SMTP_PORT = os.getenv('SMTP_PORT', 587)
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')

app = Flask(__name__)

# --- Batching Structures ---
alert_batch = []  # For low-rating alerts 
order_queue = Queue()  # For orders (time-based: 30s intervals)
batch_lock = threading.Lock()  # Thread safety

# --- Email Functions (Unchanged) ---
def send_email(alerts):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = 'Kitchen Management - Low Rating Alerts'
        body = "The following products have received bad reviews:\n\n"
        for alert in alerts:
            body += f"- {alert['menu_item_id']} (Rating: {alert['average_rating']}/5)\n"
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"Email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_email_order(body_order):
    try:
        msg_order = MIMEMultipart()
        msg_order['From'] = SENDER_EMAIL
        msg_order['To'] = RECIPIENT_EMAIL
        msg_order['Subject'] = "Kitchen Management - Weekly Ingredient Orders Status"
        msg_order.attach(MIMEText(body_order, 'plain'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
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
        alert_batch.append(alert_msg)
        if len(alert_batch) >= 2:  # Batch size = 2
            send_email(alert_batch)
            alert_batch.clear()
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")

# --- Order Consumer (Time-Based) ---
def flush_order_batch():
    """Send all orders every 30 seconds (if non-empty)."""
    with batch_lock:
        if order_queue.empty():
            return
        
        orders = []
        while not order_queue.empty():
            orders.append(order_queue.get())
        
        success_orders = [o for o in orders if o.get("status") != "error"]
        failed_orders = [o for o in orders if o.get("status") == "error"]

        if success_orders or failed_orders:
            body_order = (
                "Status: Success\n================\n" +
                "\n".join(
                    f"Message: {o.get('message', 'No details')}\n"
                    f"Supplier: {o.get('supplier', 'N/A')}\n"
                    f"Ingredient: {o.get('ingredient', 'N/A')}\n"
                    f"Trace ID: {o.get('trace_id', 'N/A')}\n----------------"
                    for o in success_orders
                ) +
                "\n\nStatus: Failure\n================\n" +
                "\n".join(
                    f"Error: {o.get('message', 'No details')}\n"
                    f"Supplier: {o.get('supplier', 'N/A')}\n"
                    f"Ingredient: {o.get('ingredient', 'N/A')}\n"
                    f"Trace ID: {o.get('trace_id', 'N/A')}\n----------------"
                    for o in failed_orders
                ) +
                f"\n\nSummary - Success: {len(success_orders)}, Failed: {len(failed_orders)}"
            )
            send_email_order(body_order)

def start_batch_timer():
    """Trigger batch processing every 30 seconds."""
    while True:
        time.sleep(30)
        flush_order_batch()

def process_notification_order(ch, method, properties, body_order):
    """Add orders to queue (time-based batching)."""
    try:
        notification_data = json.loads(body_order)
        with batch_lock:
            order_queue.put(notification_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing order: {str(e)}")

# --- RabbitMQ Setup ---
def listen_to_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
    channel = connection.channel()
    channel.queue_declare(queue='feedback_alert', durable=True)
    channel.basic_consume(queue='feedback_alert', on_message_callback=callback)
    print("Waiting for feedback alerts. To exit press CTRL+C")
    channel.start_consuming()

def start_amqp_consumer():
    purged = False
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="host.docker.internal"))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            if not purged:
                channel.queue_purge(queue=QUEUE_NAME)
                purged = True
                print(f" [*] Purged all messages from {QUEUE_NAME}")
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_notification_order)
            print(" [*] Waiting for new messages. To exit press CTRL+C")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print(" [X] Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    threading.Thread(target=start_batch_timer, daemon=True).start()
    threading.Thread(target=listen_to_queue, daemon=True).start()  # Alerts 
    threading.Thread(target=start_amqp_consumer, daemon=True).start()  # Orders 
    
    app.run(host='0.0.0.0', port=5021)