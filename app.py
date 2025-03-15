from flask import Flask, request, jsonify, render_template
import requests
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONFIG
from models import db,Menu,MenuIngredient,OrderFulfillment

app = Flask(__name__)

# URLs for external services
ORDER_FULFILLMENT_SERVICE_URL = "http://localhost:5003"
MENU_SERVICE_URL = "http://localhost:5002"
# Initialize SQLAlchemy instances
# Configuration for Menu Service database
app.config['SQLALCHEMY_BINDS'] = {
    'menu_db': f"mysql+mysqlconnector://{DATABASE_CONFIG['menu_db']['user']}:{DATABASE_CONFIG['menu_db']['password']}@{DATABASE_CONFIG['menu_db']['host']}:{DATABASE_CONFIG['menu_db']['port']}/{DATABASE_CONFIG['menu_db']['database']}",
    'order_fulfillment_db': f"mysql+mysqlconnector://{DATABASE_CONFIG['order_fulfillment_db']['user']}:{DATABASE_CONFIG['order_fulfillment_db']['password']}@{DATABASE_CONFIG['order_fulfillment_db']['host']}:{DATABASE_CONFIG['order_fulfillment_db']['port']}/{DATABASE_CONFIG['order_fulfillment_db']['database']}",
    'inventory_db': f"mysql+mysqlconnector://{DATABASE_CONFIG['inventory_db']['user']}:{DATABASE_CONFIG['inventory_db']['password']}@{DATABASE_CONFIG['inventory_db']['host']}:{DATABASE_CONFIG['inventory_db']['port']}/{DATABASE_CONFIG['inventory_db']['database']}"
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/menu/all", methods=["GET"])
def get_all_menu_items():
    try:
        # Fetch menu items via Order Fulfillment Service
        response = requests.get(f"{MENU_SERVICE_URL}/menu/all")
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create_order", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        customer_id = data["customer_id"]
        menu_item_ids = data["menu_item_ids"]

        # Create order via Order Fulfillment Service
        payload = {"customer_id": customer_id, "menu_item_ids": menu_item_ids}
        response = requests.post(f"{ORDER_FULFILLMENT_SERVICE_URL}/order-fulfillment/create-order", json=payload)
        response.raise_for_status()

        return jsonify(response.json()), 201
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/track_order/<int:order_id>", methods=["GET"])
def track_order(order_id):
    try:
        # Fetch order status via Order Fulfillment Service
        response = requests.get(f"{ORDER_FULFILLMENT_SERVICE_URL}/order-fulfillment/get-order/{order_id}")
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        # Query a single record from the database
        menu_item = Menu.query.first()
        if menu_item:
            return jsonify({"message": "Database connection successful"}), 200
        else:
            return jsonify({"message": "No data found in Menu table"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/cart')
def cart():
    return render_template('cart.html')
if __name__ == "__main__":
    app.run(debug=True)
