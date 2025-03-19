from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import json
from os import environ
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/is213_restocking"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database Models
class Supplier(db.Model):
    __tablename__ = "Suppliers"
    SupplierID = db.Column(db.Integer, primary_key=True)
    SupplierName = db.Column(db.String(255), nullable=False)
    Address = db.Column(db.String(255))
    ContactInfo = db.Column(db.String(255))

class Ingredient(db.Model):
    __tablename__ = "Ingredients"
    IngredientID = db.Column(db.Integer, primary_key=True)
    IngredientName = db.Column(db.String(255), nullable=False)

class SupplierIngredient(db.Model):
    __tablename__ = "SupplierIngredient"
    IngredientID = db.Column(db.Integer, db.ForeignKey("Ingredients.IngredientID"), primary_key=True)
    SupplierID = db.Column(db.Integer, db.ForeignKey("Suppliers.SupplierID"), primary_key=True)
    Priority = db.Column(db.Integer, nullable=False)

# AMQP configuration
RABBITMQ_HOST = environ.get("RABBITMQ_HOST") or "localhost"
QUEUE_FROM_INVENTORY = "restocking_queue"
QUEUE_TO_ORDER_SUPPLY = "order_supply_queue"

def send_to_order_supply(message):
    """Send a message to the Order Supply Service via AMQP."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_TO_ORDER_SUPPLY)
    channel.basic_publish(exchange="", routing_key=QUEUE_TO_ORDER_SUPPLY, body=json.dumps(message))
    connection.close()
    print(f" [Restocking Service] Sent to Order Supply: {message}")

def process_restock_request(ingredient_name, amount_needed):
    """Process a restock request by finding the preferred supplier and sending an order request."""
    # Push the Flask application context
    with app.app_context():  # <-- NEW: Added application context
        # Find the ingredient ID
        ingredient = db.session.scalar(db.select(Ingredient).filter_by(IngredientName=ingredient_name))
        if not ingredient:
            print(f" [Restocking Service] Ingredient not found: {ingredient_name}")
            return
        
        # Find suppliers in priority order
        supplier_relations = db.session.scalars(
            db.select(SupplierIngredient).filter_by(IngredientID=ingredient.IngredientID).order_by(SupplierIngredient.Priority.asc())
        ).all()
        
        if not supplier_relations:
            print(f" [Restocking Service] No suppliers available for ingredient: {ingredient_name}")
            return
        
        # Send the order request to the Order Supply Service via AMQP
        for supplier_relation in supplier_relations:
            supplier = db.session.get(Supplier, supplier_relation.SupplierID)
            
            # Prepare order data
            order_data = {
                "supplier_name": supplier.SupplierName,
                "ingredient_name": ingredient_name,
                "amount_needed": amount_needed
            }
            
            # Send the order data to the Order Supply Service
            send_to_order_supply(order_data)
            print(f" [Restocking Service] Order request sent for {amount_needed} of {ingredient_name} from {supplier.SupplierName} to Order Supply Service")
            return

def start_amqp_consumer():
    """Start consuming messages from the Inventory Service's AMQP queue."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_FROM_INVENTORY)

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body)
            ingredient_name = data.get("ingredient_name")
            amount_needed = data.get("amount_needed")
            print(f" [Restocking Service] Received restock request: {ingredient_name}, {amount_needed}")
            process_restock_request(ingredient_name, amount_needed)
        except Exception as e:
            print(f" [Restocking Service] Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_FROM_INVENTORY, on_message_callback=callback)
    print(" [Restocking Service] Waiting for restocking requests...")
    channel.start_consuming()

if __name__ == "__main__":
    # Start the AMQP consumer in a separate thread
    amqp_thread = threading.Thread(target=start_amqp_consumer)
    amqp_thread.daemon = True
    amqp_thread.start()

    # Start the Flask app
    app.run(host="0.0.0.0", port=5005, debug=True)