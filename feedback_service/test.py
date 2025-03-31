# Used for testing notifications send to email, change the recipient_email
import pika
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import threading
import time

# Mailgun SMTP Settings
SMTP_SERVER = 'in-v3.mailjet.com'
SMTP_PORT = 587  # Use 465 for SSL if needed
SMTP_USERNAME = '3db3fcf147025c7ab9a24e9e8f75dd62'  # Replace with your Mailjet API key
SMTP_PASSWORD = '6c0fda3a2887782d20fde64e1c07b043'  # Replace with your Mailjet API secret
SENDER_EMAIL = 'yuyaoxuan888@gmail.com'  # Use your verified Mailjet sender email
RECIPIENT_EMAIL = 'yaoxuan.yu.2023@scis.smu.edu.sg'


# To accumulate alerts
alert_batch = []

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

# Setup RabbitMQ connection
def listen_to_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))  # Use the correct RabbitMQ host
    channel = connection.channel()

    # Declare the queue to ensure it exists
    channel.queue_declare(queue='feedback_alert', durable=True)

    # Set up the consumer
    channel.basic_consume(queue='feedback_alert', on_message_callback=callback)

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    listen_to_queue()
