from flask import Flask, jsonify
import sys
sys.path.append('..')
from config import DATABASE_CONFIG
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
import requests
# Configure Menu Service database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['menu_db']['user']}:{DATABASE_CONFIG['menu_db']['password']}@{DATABASE_CONFIG['menu_db']['host']}:{DATABASE_CONFIG['menu_db']['port']}/{DATABASE_CONFIG['menu_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Menu(db.Model):
    __tablename__ = 'Menu'
    MenuItemID = db.Column(db.Integer, primary_key=True)
    ItemName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    Price = db.Column(db.Float, nullable=False)
    AvailabilityStatus = db.Column(db.Boolean, default=True)
class MenuIngredient(db.Model):
    # Bind this model to the menu_db
    __tablename__ = 'MenuIngredient'
    MenuItemID = db.Column(db.Integer, nullable=False)
    IngredientID = db.Column(db.Integer, nullable=False)
    QuantityRequired = db.Column(db.Float, nullable=False)
    __table_args__ = (db.PrimaryKeyConstraint('MenuItemID', 'IngredientID'),)
    

@app.route('/menu/all', methods=['GET'])
def get_all_menu_items():
    try:
        # Fetch all menu items and their ingredients
        menu_items = Menu.query.all()
        menu_ingredients = MenuIngredient.query.all()

        # Create a dictionary to store the ingredients for each menu item
        ingredients_dict = {}
        for ingredient in menu_ingredients:
            if ingredient.MenuItemID not in ingredients_dict:
                ingredients_dict[ingredient.MenuItemID] = []
            ingredients_dict[ingredient.MenuItemID].append(ingredient)

        # Batch request to Inventory Service
        ingredient_ids = {ingredient.IngredientID for ingredient in menu_ingredients}
        inventory_response = requests.post("http://localhost:5004/inventory/batch", json={"ingredient_ids": list(ingredient_ids)})
        inventory_data = inventory_response.json() if inventory_response.status_code == 200 else {}

        # Check ingredient availability for each menu item
        result = []
        for item in menu_items: 
            is_available = True
            if item.MenuItemID in ingredients_dict:
                for ingredient in ingredients_dict[item.MenuItemID]:
                    if inventory_data.get(str(ingredient.IngredientID), 0) < ingredient.QuantityRequired:
                        is_available = False
                        break

            # Update availability status based on ingredient check
            item.AvailabilityStatus = is_available

            result.append({
                "id": item.MenuItemID,
                "name": item.ItemName,
                "description": item.Description,
                "price": item.Price,
                "availability_status": item.AvailabilityStatus
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/menu/item/<int:itemID>', methods=['GET'])
def get_menu_item_details(itemID):
    try:
        menu_item = Menu.query.filter_by(MenuItemID=itemID).first()
        if menu_item:
            result = {
                "id": menu_item.MenuItemID,
                "name": menu_item.ItemName,
                "description": menu_item.Description,
                "price": menu_item.Price,
                "availability_status": menu_item.AvailabilityStatus
            }
            return jsonify(result), 200
        else:
            return jsonify({"error": f"Menu item with ID {itemID} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
