from flask import Flask, request, jsonify
import requests
import sys
sys.path.append('..')
from config import DATABASE_CONFIG
from flask_sqlalchemy import SQLAlchemy
import random

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
# @app.route("/order-fulfillment/menu/all", methods=["GET"])
# def get_all_menu_items():
#     try:
#         # Proxy request to Menu Service
#         response = requests.get(f"{MENU_SERVICE_URL}/menu/all")
#         response.raise_for_status()
#         return jsonify(response.json()), 200
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/order-fulfillment/create-order', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        customer_id = data["customer_id"]
        menu_item_ids = ",".join([str(id) for id in data["menu_item_ids"]])  # Convert list to comma-separated string
        total_price = data["total_price"]
        station_id = random.choice([101,102,103]) # Assume station ID is provided in the request

        # Create a new order in the database
        new_order = OrderFulfillment(
            CustomerID=customer_id,
            MenuItemIDs=menu_item_ids,
            TotalPrice=total_price,
            OrderStatus="Pending",
            AssignedStationID=station_id
        )
        db.session.add(new_order)
        db.session.commit()

        # Invoke Kitchen Station Service to assign the task
        kitchen_station_url = "http://localhost:5008/kitchen/assign"
        payload = {
            "order_id": new_order.OrderID,
            "station_id": station_id
        }
        response = requests.post(kitchen_station_url, json=payload)

        if response.status_code == 201:
            return jsonify({"message": "Order created and task assigned successfully", "order_id": new_order.OrderID}), 201
        else:
            return jsonify({"message": "Order created but failed to assign task", "order_id": new_order.OrderID}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/order-fulfillment/<int:orderID>', methods=['GET'])
def get_order_id(orderID):
    try:
        order = OrderFulfillment.query.filter_by(OrderID=orderID).first()
        if order:
            result = {
                "id": order.OrderID,
                "customer_id": order.CustomerID,
                "menu_item_ids": order.MenuItemIDs,
                "total_price": order.TotalPrice,
                "order_status": order.OrderStatus,
                "assigned_station_id": order.AssignedStationID,
                "notification_sent": order.NotificationSent,
                "created_at": order.CreatedAt.strftime('%Y-%m-%d %H:%M:%S')
            }
            return jsonify(result), 200
        else:
            return jsonify({"error": f"Menu item with ID {orderID} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
