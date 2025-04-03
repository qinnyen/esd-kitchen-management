from flask import Flask, request, jsonify
import requests
import sys
# sys.path.append('..')
from config import DATABASE_CONFIG
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
# Configure Menu Service database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['order_fulfillment_db']['user']}:{DATABASE_CONFIG['order_fulfillment_db']['password']}@{DATABASE_CONFIG['order_fulfillment_db']['host']}:{DATABASE_CONFIG['order_fulfillment_db']['port']}/{DATABASE_CONFIG['order_fulfillment_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# URL for Menu Service
# MENU_SERVICE_URL = "http://localhost:5002"
ORDER_SERVICE_CREATE = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1/CreateOrder/"
ORDER_SERVICE_READ = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1/Orders"
ORDER_SERVICE_UPDATE = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1/UpdateOrder/"
ORDER_SERVICE_DELETE = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1/DeleteOrder/"
ORDER_SERVICE_URL = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1/OrdersByCustomerID/"
# KITCHEN_SERVICE_URL = "http://localhost:5008"
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://host.docker.internal:5002")
KITCHEN_SERVICE_URL = os.getenv("KITCHEN_SERVICE_URL", "http://host.docker.internal:5008")


db = SQLAlchemy(app)
class OrderFulfillment(db.Model):
    __tablename__ = 'OrderFulfillment'
    OrderID = db.Column(db.Integer, primary_key=True)
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
        print(data)
        customer_id = data["customer_id"]
        menu_item_ids = data["menu_item_ids"]  # Convert list of dicts to comma-separated string of ids
        menu_item_ids2 = ",".join([str(item["MenuItemID"]) for item in menu_item_ids])
        total_price = data["total_price"]
        headers = {'Content-Type': 'application/json'}
        ordersData = {
            "CustomerID": customer_id,
            "MenuItems": menu_item_ids,
            "TotalPrice": total_price
        }
        print(ordersData)
        station_id = random.choice([101,102,103]) # Assume station ID is provided in the request
        response = requests.post(ORDER_SERVICE_CREATE, json=ordersData, headers=headers)
        if response.status_code == 200:
            response.json()
            print(response.json())

            # Create a new order in the database
            new_order = OrderFulfillment(
                OrderID=response.json(), 
                CustomerID=customer_id,
                MenuItemIDs=menu_item_ids2,
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
        else:
            return jsonify({"error": "Failed to create order in external service"}), response.status_code
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

# Endpoint: Retrieve orders by customer ID (Composite Service)
@app.route('/order-fulfillment/customer/<int:customer_id>', methods=['GET'])
def get_order_status(customer_id):
    try:

        response = requests.get(f"{ORDER_SERVICE_URL}/{customer_id}")
        menu_ids = response.json()["MenuItemIDs"]
        menu_ids_list = [int(x) for x in menu_ids.split(",")]
        menu_items = []
        menuItems = requests.get(f"{MENU_SERVICE_URL}/menu/items/{menu_ids}")
        menu_items = menuItems.json()
        
        # menu_items = []
        # for i in menu_ids_list:
        #      menuItems = requests.get(f"{MENU_SERVICE_URL}/menu/item/{i}")
        #      menu_items.append(menuItems.json())

             
        order_response = response.json()
        order_response["MenuItems"] = menu_items

        if response.status_code == 200:
            return jsonify(order_response), 200
        else:
            return jsonify({"error": "Failed to retrieve orders"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/order-fulfillment/update-order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.get_json()
        new_status = data["order_status"]
        response = requests.put(f"{ORDER_SERVICE_UPDATE}/{order_id}", json={"order_status": new_status})
        if response.status_code == 200:
            order = OrderFulfillment.query.filter_by(OrderID=order_id).first()
            if order:
                order.OrderStatus = new_status
                db.session.commit()
                return jsonify({"message": "Order status updated successfully"}), 200
            else:
                return jsonify({"error": "Order not found"}), 404
        else:
            return jsonify({"error": "Failed to update order in external service"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/order-fulfillment/kitchen/stations', methods=['GET'])
def kitchen():
    try:
        response = requests.get(f"{KITCHEN_SERVICE_URL}/kitchen/stations")
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Failed to fetch kitchen stations"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/order-fulfillment/kitchen/task/<int:task_id>/<int:order_id>', methods=['PUT'])
def update_task_progress_with_order(task_id, order_id):
    try:
        data = request.get_json()
        new_status = data["task_status"]
        
        # Send the PUT request to the kitchen service
        kitchen_response = requests.put(f"{KITCHEN_SERVICE_URL}/kitchen/task/{task_id}", json={"task_status": new_status})
        
        if kitchen_response.status_code == 200:
            order = OrderFulfillment.query.filter_by(OrderID=order_id).first()
            if order:
                order.OrderStatus = new_status
                db.session.commit()
                
                # Update the order status in the external order service
                order_res = requests.put(f"{ORDER_SERVICE_UPDATE}/{order_id}", json={"OrderStatus": new_status})
                if order_res.status_code != 200:
                    return jsonify({"message": "Task status updated in kitchen but failed to update in order service"}), 500
            else:
                return jsonify({"error": "Order not found"}), 404

            # Return the JSON content of the kitchen response
            return jsonify(kitchen_response.json()), 200
        else:
            return jsonify({"error": "Failed to update task status in external service"}), kitchen_response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=True)
