from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
import pika
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import threading

# sys.path.append('..')
from config import DATABASE_CONFIG

app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['inventory_db']['user']}:{DATABASE_CONFIG['inventory_db']['password']}@{DATABASE_CONFIG['inventory_db']['host']}:{DATABASE_CONFIG['inventory_db']['port']}/{DATABASE_CONFIG['inventory_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Shut down the scheduler when the app exits
atexit.register(lambda: scheduler.shutdown())

class Inventory(db.Model):
    __tablename__ = 'Inventory'
    IngredientID = db.Column(db.Integer, primary_key=True)
    IngredientName = db.Column(db.String(100), nullable=False)
    QuantityAvailable = db.Column(db.Integer, nullable=False)
    UnitOfMeasure = db.Column(db.String(50), nullable=False)
    ExpiryDate = db.Column(db.Date, nullable=False)
    ReorderThreshold = db.Column(db.Integer, nullable=False)

# AMQP configuration for Restocking Service
RABBITMQ_HOST = "host.docker.internal"
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
        # Return a success response
        return jsonify({"success": True, "message": "Restock request sent successfully"}), 200
    except Exception as e:
        # Handle connection errors or other exceptions
        print(f" [Inventory Service] Error sending restock request: {e}")
        return jsonify({"success": False, "message": f"Error sending restock request: {str(e)}"}), 500

def check_and_notify_low_stock():
    """Check for low stock items within Flask app context."""
    with app.app_context():  # <-- Add this wrapper
        try:
            low_stock_items = Inventory.query.filter(
                Inventory.QuantityAvailable <= Inventory.ReorderThreshold
            ).all()
            if not low_stock_items:
                print(" [Inventory Service] No low stock items found.")
                return
            for item in low_stock_items:
                amount_needed = item.ReorderThreshold - item.QuantityAvailable
                send_restock_request(item.IngredientName, amount_needed, item.UnitOfMeasure)
        except Exception as e:
            print(f" [Inventory Service] Error checking low stock: {e}")

# Schedule the job (adjust interval for testing/production)
def schedule_low_stock_check(interval_seconds=15):  # Default: 15 seconds for testing
    """Schedule the low-stock check job with a configurable interval."""
    trigger = IntervalTrigger(seconds=interval_seconds)  # Change to `weeks=1` for production
    scheduler.add_job(
        func=check_and_notify_low_stock,
        trigger=trigger,
        id="low_stock_check",
        replace_existing=True,
    )
    print(f" [Scheduler] Low-stock check scheduled every {interval_seconds} second(s).")

# Start the scheduler when the app runs
schedule_low_stock_check(interval_seconds=15)  # Set to 5 seconds for testing

@app.route("/inventory/restock/", methods=["POST"])
def send_restock_request_http(): 
    """
    Send a restock request to the Restocking Service via AMQP.
    """
    data = request.get_json()
    restock_response = send_restock_request(
        ingredient_name=data.get("ingredient_name"),
        amount_needed=data.get("amount_needed"),
        unit_of_measure=data.get("unit_of_measure")
    )
      # If the request was successful, return a success response
    if restock_response[1] != 200:
        return jsonify({"success": False, "message": "Failed to send restock request"}), 500
    return restock_response


    # # Uncomment this block if you want to use RabbitMQ directly in the HTTP endpoint
    
    
    
    
    # try:
    #     # Create a connection to RabbitMQ
    #     connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    #     channel = connection.channel()
    #     # Prepare the message
    #     data = request.get_json()
 
    #     ingredient_name = data.get("ingredient_name")
    #     amount_needed = data.get("amount_needed")
    #     unit_of_measure = data.get("unit_of_measure")
    #     message = {
    #     "ingredient_name": ingredient_name,
    #     "amount_needed": amount_needed,
    #     "unit_of_measure": unit_of_measure
    #     }
        


    #     # Declare the queue (in case it doesn't exist)
    #     channel.queue_declare(queue=QUEUE_TO_RESTOCKING)

    #     # Publish the message to the queue
    #     channel.basic_publish(
    #         exchange="",
    #         routing_key=QUEUE_TO_RESTOCKING,
    #         body=json.dumps(message)
    #     )
    #     print(f" [Inventory Service] Sent to restocking_queue: {message}")
    #     connection.close()
    #     return jsonify({"success": True, "message": "Restock request sent successfully"}), 200
    # except Exception as e:
    #     print(f" [Inventory Service] Error sending restock request: {e}")
    #     return jsonify({"success": False, "message": f"Error sending restock request: {str(e)}"}), 500

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
            str(item.IngredientID): {
                "name": item.IngredientName,
                "quantity_available": item.QuantityAvailable,
                "unit_of_measure": item.UnitOfMeasure,
                "expiry_date": item.ExpiryDate.strftime('%Y-%m-%d'),
                "reorder_threshold": item.ReorderThreshold
            }
            for item in ingredients
        }
        if not result:
            return jsonify({"error": "No ingredients found for the provided IDs"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RFID event handler, process RFID events and updates inventory_service, updates restocking if needed
def handle_rfid_event(ch, method, properties, body):
    try:
        data = json.loads(body)
        if data.get("event_type") == "ingredient_used":
            ingredient_id = data["ingredient_id"]
            quantity_used = data["quantity_used"]

            with app.app_context():
                ingredient = Inventory.query.filter_by(IngredientID=ingredient_id).first()
                if ingredient:
                    ingredient.QuantityAvailable -= quantity_used
                    db.session.commit()
                    print(f"[Inventory] Updated stock for IngredientID {ingredient_id}: -{quantity_used}")

                    # Trigger restocking when stock hits 0
                    if ingredient.QuantityAvailable == 0:
                        send_restock_request(
                            ingredient_name=ingredient.IngredientName,
                            amount_needed=ingredient.ReorderThreshold - ingredient.QuantityAvailable,
                            unit_of_measure=ingredient.UnitOfMeasure
                        )
                else:
                    print(f"[Inventory] Ingredient ID {ingredient_id} not found.")

    except Exception as e:
        print(f"[Inventory] Error processing RFID event: {e}")

# consumer starter, listens for RFID events
def start_rfid_consumer():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue="rfid_events_queue", durable=True)
        channel.basic_consume(queue="rfid_events_queue", on_message_callback=handle_rfid_event, auto_ack=True)
        print("[Inventory] RFID consumer started.")
        channel.start_consuming()
    except Exception as e:
        print(f"[Inventory] RFID consumer failed: {e}")

if __name__ == "__main__":
    threading.Thread(target=start_rfid_consumer, daemon=True).start()  #start RFID event consumer in background
    app.run(host="0.0.0.0", port=5004, debug=False) #Debug set to false to prevent duplication of cron jobs