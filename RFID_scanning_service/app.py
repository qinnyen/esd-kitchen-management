from flask import Flask, request, jsonify
import pika
import json
import os

app = Flask(__name__)

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "host.docker.internal")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RFID_EVENTS_QUEUE = "rfid_events_queue"

# Helper: Emit AMQP Event
def emit_rfid_event(ingredient_id, quantity_used):
    """
    Publishes an 'ingredient_used' event to the RFID event queue.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        channel = connection.channel()
        channel.queue_declare(queue=RFID_EVENTS_QUEUE, durable=True)

        event_payload = {
            "event_type": "ingredient_used",
            "ingredient_id": ingredient_id,
            "quantity_used": quantity_used
        }

        channel.basic_publish(
            exchange='',
            routing_key=RFID_EVENTS_QUEUE,
            body=json.dumps(event_payload),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )

        print(f"[RFID] Event published: {event_payload}")
        connection.close()
        return True
    except Exception as e:
        print(f"[RFID] Failed to publish event: {e}")
        return False

# API Route: Simulate RFID Scan
@app.route("/rfid/scan", methods=["POST"])
def scan_rfid_tag():
    """
    Simulates an RFID tag scan. 
    Expects JSON: { "ingredient_id": int, "quantity_used": int }
    """
    try:
        data = request.get_json()
        ingredient_id = int(data["ingredient_id"])
        quantity_used = int(data.get("quantity_used", 1))  # Default to 1 if not provided

        success = emit_rfid_event(ingredient_id, quantity_used)

        if success:
            return jsonify({"message": "RFID event sent to inventory service."}), 200
        else:
            return jsonify({"error": "Failed to emit RFID event."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=True)
