from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pika
import json
import requests
from config import DATABASE_CONFIG

INVENTORY_SERVICE_URL = "http://inventory_service:5004/inventory"
RABBITMQ_HOST = "rabbitmq"
LOW_STOCK_THRESHOLD = 10  

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['rfid_db']['user']}:{DATABASE_CONFIG['rfid_db']['password']}@{DATABASE_CONFIG['rfid_db']['host']}:{DATABASE_CONFIG['rfid_db']['port']}/{DATABASE_CONFIG['rfid_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Logs each scan with details of ingredient, station, and time
class RFIDEvent(db.Model):
    __bind_key__ = 'rfid'
    __tablename__ = "RFIDEvent"
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, nullable=False)
    station_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)  # e.g. "used", "picked"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Used to fetch the current stock of ingredients for decision-making
class Inventory(db.Model):
    __bind_key__ = 'inventory'
    __tablename__ = "Ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity_available = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(20), nullable=False)

# Log RFID Scan + Update Inventory + Check for Low Stock
@app.route("/rfid/scan", methods=["POST"])
def scan_rfid():
    """
    Accepts a scan event in this format:
    {
        "ingredient_id": 1,
        "station_id": 101,
        "action": "used"
    }
    Logs the event, checks the ingredient level, and alerts if stock is low.
    """
    try:
        data = request.get_json()
        required = ["ingredient_id", "station_id", "action"]
        missing = [f for f in required if f not in data]

        if missing:
            return jsonify({"error": "Missing field(s)", "fields": missing}), 400

        # Log the scan
        event = RFIDEvent(
            ingredient_id=data["ingredient_id"],
            station_id=data["station_id"],
            action=data["action"]
        )
        db.session.add(event)
        db.session.commit()

        # If action is "used", check inventory via HTTP
        if data["action"].lower() == "used":
            try:
                response = requests.get(f"{INVENTORY_SERVICE_URL}/{data['ingredient_id']}")
                if response.status_code == 200:
                    inventory = response.json()
                    new_qty = inventory["quantity_available"] - 1  # Simulated deduction

                    print(f"[RFID] {inventory['name']} used. New (simulated) qty: {new_qty}")

                    # 3. Trigger LowStockAlert if under threshold
                    if new_qty <= LOW_STOCK_THRESHOLD:
                        send_low_stock_alert(
                            ingredient_id=inventory["id"],
                            ingredient_name=inventory["name"],
                            quantity=new_qty,
                            threshold=LOW_STOCK_THRESHOLD
                        )
                else:
                    print(f"[Inventory API Error] Status {response.status_code}")
            except Exception as e:
                print(f"[Inventory API Error] {e}")

        return jsonify({"message": "RFID scan processed"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_low_stock_alert(ingredient_id, ingredient_name, quantity, threshold):
    """
    Sends a message to RabbitMQ if an ingredient is detected to be low.
    The consumer (e.g., Notification or Restocking Service) can handle it.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        # Declare the alert queue (idempotent)
        channel.queue_declare(queue='low_stock_alert', durable=True)

        # Create the alert message
        alert = {
            "ingredient_id": ingredient_id,
            "ingredient_name": ingredient_name,
            "quantity": quantity,
            "threshold": threshold,
            "message": "Low stock detected via RFID"
        }

        # Send the alert message
        channel.basic_publish(
            exchange='',
            routing_key='low_stock_alert',
            body=json.dumps(alert),
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
        )
        print(f"📤 Alert sent for {ingredient_name}")
        connection.close()
    except Exception as e:
        print(f"[Alert Error] Failed to send low stock alert: {e}")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "RFID Scanning Service is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
