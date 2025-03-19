from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
import pika
import json
sys.path.append('..')
from config import DATABASE_CONFIG

app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['inventory_db']['user']}:{DATABASE_CONFIG['inventory_db']['password']}@{DATABASE_CONFIG['inventory_db']['host']}:{DATABASE_CONFIG['inventory_db']['port']}/{DATABASE_CONFIG['inventory_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Inventory(db.Model):
    __tablename__ = 'Inventory'
    IngredientID = db.Column(db.Integer, primary_key=True)
    IngredientName = db.Column(db.String(100), nullable=False)
    QuantityAvailable = db.Column(db.Integer, nullable=False)
    UnitOfMeasure = db.Column(db.String(50), nullable=False)
    ExpiryDate = db.Column(db.Date, nullable=False)
    ReorderThreshold = db.Column(db.Integer, nullable=False)

# AMQP configuration for Restocking Service
RABBITMQ_HOST = "localhost"
QUEUE_TO_RESTOCKING = "restocking_queue"

def send_restock_request(ingredient_name, amount_needed, unit_of_measure):
    """
    Send a restock request to the Restocking Service via AMQP.
    """
    try:
        # Create a connection to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()

        # Declare the queue (in case it doesn't exist)
        channel.queue_declare(queue=QUEUE_TO_RESTOCKING)

        # Prepare the message
        message = {
            "ingredient_name": ingredient_name,
            "amount_needed": amount_needed,
            "unit_of_measure": unit_of_measure
        }

        # Publish the message to the queue
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_TO_RESTOCKING,
            body=json.dumps(message)
        )
        print(f" [Inventory Service] Sent to restocking_queue: {message}")
        connection.close()
    except Exception as e:
        print(f" [Inventory Service] Error sending restock request: {e}")

def check_and_notify_low_stock():
    """
    Check for low stock items and send restock requests via AMQP.
    """
    try:
        # Fetch ingredients below the reorder threshold
        low_stock_items = Inventory.query.filter(Inventory.QuantityAvailable <= Inventory.ReorderThreshold).all()

        if not low_stock_items:
            print(" [Inventory Service] No low stock items found.")
            return

        # Send a restock request for each low stock item
        for item in low_stock_items:
            amount_needed = item.ReorderThreshold - item.QuantityAvailable
            send_restock_request(item.IngredientName, amount_needed, item.UnitOfMeasure)
    except Exception as e:
        print(f" [Inventory Service] Error checking low stock: {e}")

# New endpoint to trigger weekly low stock notifications for restocking service
@app.route('/inventory/notify_low_stock', methods=['POST'])
def notify_low_stock():
    """
    Endpoint to trigger low stock notifications.
    """
    try:
        check_and_notify_low_stock()
        return jsonify({"message": "Low stock notifications sent successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/<int:ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    try:
        ingredient = Inventory.query.filter_by(IngredientID=ingredient_id).first()
        if ingredient:
            result = {
                "ingredient_id": ingredient.IngredientID,
                "name": ingredient.IngredientName,
                "quantity_available": ingredient.QuantityAvailable,
                "unit_of_measure": ingredient.UnitOfMeasure,
                "expiry_date": ingredient.ExpiryDate.strftime('%Y-%m-%d'),
                "reorder_threshold": ingredient.ReorderThreshold
            }
            return jsonify(result), 200
        else:
            return jsonify({"error": "Ingredient not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/update/<int:ingredient_id>', methods=['PUT'])
def update_stock_level(ingredient_id):
    try:
        data = request.get_json()
        quantity_change = data.get('quantity_change', 0)

        ingredient = Inventory.query.filter_by(IngredientID=ingredient_id).first()
        if ingredient:
            ingredient.QuantityAvailable += quantity_change
            db.session.commit()
            return jsonify({"message": "Stock level updated successfully"}), 200
        else:
            return jsonify({"error": "Ingredient not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/all', methods=['GET'])
def get_all_stocks():
    try:
        # Fetch all inventory items
        inventory_items = Inventory.query.all()
        result = [
            {
                "ingredient_id": item.IngredientID,
                "name": item.IngredientName,
                "quantity_available": item.QuantityAvailable,
                "unit_of_measure": item.UnitOfMeasure,
                "expiry_date": item.ExpiryDate.strftime('%Y-%m-%d'),
                "reorder_threshold": item.ReorderThreshold
            }
            for item in inventory_items
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/alert', methods=['POST'])
def low_stock_alerts():
    try:
        # Fetch ingredients below the reorder threshold
        low_stock_items = Inventory.query.filter(Inventory.QuantityAvailable <= Inventory.ReorderThreshold).all()
        
        if not low_stock_items:
            return jsonify({"message": "No low stock items found."}), 200
        
        # Example: Trigger notification or log an alert (mock implementation)
        alerts = []
        for item in low_stock_items:
            alert_message = f"Low stock alert for {item.IngredientName}: Only {item.QuantityAvailable} {item.UnitOfMeasure} left!"
            alerts.append(alert_message)
        
        # Return the alerts as a response (or integrate with Notification Service here)
        return jsonify({"alerts": alerts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/low_stock', methods=['GET'])
def get_low_stock_items():
    try:
        low_stock_items = Inventory.query.filter(Inventory.QuantityAvailable <= Inventory.ReorderThreshold).all()
        result = [
            {
                "ingredient_id": item.IngredientID,
                "name": item.IngredientName,
                "quantity_available": item.QuantityAvailable,
                "reorder_threshold": item.ReorderThreshold
            }
            for item in low_stock_items
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/inventory/batch', methods=['POST'])
def get_batch_ingredients():
    try:
        data = request.get_json()
        ingredient_ids = data.get('ingredient_ids', [])
        
        if not ingredient_ids:
            return jsonify({"error": "No ingredient IDs provided"}), 400
        
        ingredients = Inventory.query.filter(Inventory.IngredientID.in_(ingredient_ids)).all()
        result = {
            str(item.IngredientID): item.QuantityAvailable
            for item in ingredients
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)