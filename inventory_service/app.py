from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
