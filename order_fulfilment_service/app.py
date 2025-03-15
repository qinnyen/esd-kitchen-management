from flask import Flask, request, jsonify
import requests
import sys
sys.path.append('..')
from config import DATABASE_CONFIG
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
# Configure Menu Service database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['order_fulfillment_db']['user']}:{DATABASE_CONFIG['order_fulfillment_db']['password']}@{DATABASE_CONFIG['order_fulfillment_db']['host']}:{DATABASE_CONFIG['order_fulfillment_db']['port']}/{DATABASE_CONFIG['order_fulfillment_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# URL for Menu Service
MENU_SERVICE_URL = "http://localhost:5002"
db = SQLAlchemy(app)
class OrderFulfillment(db.Model):
    __tablename__ = 'OrderFulfillment'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CustomerID = db.Column(db.Integer, nullable=False)
    MenuItemIDs = db.Column(db.String(255), nullable=False)
    TotalPrice = db.Column(db.Float, nullable=False)
    OrderStatus = db.Column(db.String(50), nullable=False)
    AssignedStationID = db.Column(db.Integer, nullable=True)
    NotificationSent = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
@app.route("/order-fulfillment/menu/all", methods=["GET"])
def get_all_menu_items():
    try:
        # Proxy request to Menu Service
        response = requests.get(f"{MENU_SERVICE_URL}/menu/all")
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/order-fulfillment/create-order", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        customer_id = data["customer_id"]
        menu_item_ids = ",".join([str(id) for id in data["menu_item_ids"]])  # Convert list to comma-separated string

        # Validate menu items via Menu Service
        total_price = 0.0
        for item_id in data["menu_item_ids"]:
            response = requests.get(f"{MENU_SERVICE_URL}/menu/item/{item_id}")
            if response.status_code == 200:
                item_data = response.json()
                total_price += item_data["price"]
            else:
                return jsonify({"error": f"Menu item ID {item_id} is invalid"}), 400

        # Create a new order in the database
        new_order = OrderFulfillment(
            CustomerID=customer_id,
            MenuItemIDs=menu_item_ids,
            TotalPrice=total_price,
            OrderStatus="Pending"
        )
        db.session.add(new_order)
        db.session.commit()  # Save changes to the database

        return jsonify({"message": "Order created successfully", "order_id": new_order.OrderID}), 201
    except Exception as e:
        db.session.rollback()  # Rollback changes if an error occurs
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
