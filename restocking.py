from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import json
from os import environ
import threading
from config import DATABASE_CONFIG

app = Flask(__name__)
CORS(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{DATABASE_CONFIG['restocking_db']['user']}:{DATABASE_CONFIG['restocking_db']['password']}@{DATABASE_CONFIG['restocking_db']['host']}:{DATABASE_CONFIG['restocking_db']['port']}/{DATABASE_CONFIG['restocking_db']['database']}"
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

# AMQP Setup
RABBITMQ_HOST = environ.get("RABBITMQ_HOST") or "localhost"
QUEUE_FROM_INVENTORY = "restocking_queue"
QUEUE_TO_MANAGE_INVENTORY = "manage_inventory_queue"

def send_to_manage_inventory(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_TO_MANAGE_INVENTORY,
        body=json.dumps(message)
    )
    connection.close()
    print(f" [Restocking Service] Sent to [Manage Inventory Service]: {message}")

def process_restock_request(ingredient_name, amount_needed, unit_of_measure):
    with app.app_context():
        ingredient = Ingredient.query.filter_by(IngredientName=ingredient_name).first()
        if not ingredient:
            return

        suppliers = db.session.query(Supplier)\
            .join(SupplierIngredient)\
            .filter(SupplierIngredient.IngredientID == ingredient.IngredientID)\
            .all()

        if suppliers:
            send_to_manage_inventory({
                "ingredient_name": ingredient_name,
                "amount_needed": amount_needed,
                "unit_of_measure": unit_of_measure,
                "suppliers": [s.SupplierName for s in suppliers]
            })
        else:
            print(f"No suppliers found for {ingredient_name}")

def start_amqp_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_FROM_INVENTORY)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        process_restock_request(
            data["ingredient_name"],
            data["amount_needed"],
            data["unit_of_measure"]
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_FROM_INVENTORY, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    threading.Thread(target=start_amqp_consumer, daemon=True).start()
    app.run(host="0.0.0.0", port=5005, debug=False)