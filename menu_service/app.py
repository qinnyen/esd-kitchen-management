from flask import Flask, jsonify
import sys
sys.path.append('..')
from config import DATABASE_CONFIG
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

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

@app.route('/menu/all', methods=['GET'])
def get_menu():
    try:
        # Query all menu items from the database
        menu_items = Menu.query.all()
        result = [
            {
                "id": item.MenuItemID,
                "name": item.ItemName,
                "description": item.Description,
                "price": item.Price,
                "availability_status": item.AvailabilityStatus
            }
            for item in menu_items
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/menu/item/<int:menu_item_id>', methods=['GET'])
def get_menu_item_details(menu_item_id):
    try:
        menu_item = Menu.query.filter_by(MenuItemID=menu_item_id).first()
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
            return jsonify({"error": "Menu item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/menu/ingredients/<int:menu_item_id>', methods=['GET'])
def get_ingredient_requirements(menu_item_id):
    try:
        ingredients = MenuIngredient.query.filter_by(MenuItemID=menu_item_id).all()
        if ingredients:
            result = [
                {
                    "ingredient_id": ingredient.IngredientID,
                    "quantity_required": ingredient.QuantityRequired
                }
                for ingredient in ingredients
            ]
            return jsonify(result), 200
        else:
            return jsonify({"error": "No ingredients found for this menu item"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5002, debug=True)
