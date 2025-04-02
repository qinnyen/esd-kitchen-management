from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys
import os

# Add your parent directory to the system path (if needed for config imports)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE_CONFIG

app = Flask(__name__)

CORS(app)

# Configure database connection (MySQL, consistent with your team)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['order_db']['user']}:{DATABASE_CONFIG['order_db']['password']}@{DATABASE_CONFIG['order_db']['host']}:{DATABASE_CONFIG['order_db']['port']}/{DATABASE_CONFIG['order_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define the Order model/table structure
class Order(db.Model):
    __tablename__ = 'orders'  # Ensure table name is 'Orders' in your MySQL DB
    OrderID = db.Column(db.Integer, primary_key=True)  # Auto-incremented OrderID
    CustomerID = db.Column(db.Integer, nullable=False)
    MenuItemIDs = db.Column(db.String(255), nullable=False)
    TotalPrice = db.Column(db.Float, nullable=False)
    OrderStatus = db.Column(db.String(100), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.now)  # Time of submission

@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """Get OrderID and MenuItemIDs for a specific order by OrderID."""
    # Querying the Order table to get order data based on OrderID
    order = Order.query.filter_by(OrderID=order_id).first()
    
    if order:
        # Return only the OrderID and MenuItemIDs
        return jsonify({
            "OrderID": order.OrderID,
            "MenuItemIDs": order.MenuItemIDs
        }), 200
    else:
        # If no order found for that OrderID, return an error message
        return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(port=5001, debug=True)
