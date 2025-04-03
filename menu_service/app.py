from datetime import datetime
from flask import Flask, jsonify
import sys
import os
# sys.path.append('..')
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
    
ORDER_SERVICE_URL = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1/GetOrderItems"  # Order Service URL
# INVENTORY_SERVICE_URL = "http://localhost:5004"  # Inventory Service URL  
# ERROR_RESOLUTION_URL = "http://localhost:5013"
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://host.docker.internal:5004") # Inventory Service URL  
ERROR_RESOLUTION_URL = os.getenv("ERROR_RESOLUTION_URL", "http://host.docker.internal:5013")
@app.route('/menu/<int:order_id>', methods=['GET'])
def get_menu_and_ingredients(order_id):
    try:
        # Step 1: Fetch order details from Order Service
        order_response = requests.get(f"{ORDER_SERVICE_URL}/{order_id}")
        if order_response.status_code != 200:
            return jsonify({"error": "Failed to fetch order details"}), 500

        order_data = order_response.json()
        menu_item_ids = [int(item["MenuItemID"]) for item in order_data]  # Example: [1, 2, 3]


        # Step 2: Fetch menu items and their ingredients from Menu Service

        # Fetch menu item details
        menu_items_data = Menu.query.filter(Menu.MenuItemID.in_(menu_item_ids)).all()
      
        # Fetch ingredient requirements for this menu item
        ingredients_for_menu_item = MenuIngredient.query.filter(MenuIngredient.MenuItemID.in_(menu_item_ids)).all()
        # Step 3: Query Inventory Service for detailed ingredient information
        detailed_ingredients = []
        for ingredient in ingredients_for_menu_item:
            inventory_response = requests.get(f"{INVENTORY_SERVICE_URL}/inventory/{ingredient.IngredientID}")
            if inventory_response.status_code == 200:
                inventory_data = inventory_response.json()
                detailed_ingredients.append({
                    "name": inventory_data["name"],
                    "unit_of_measure": inventory_data["unit_of_measure"],
                    "quantity_required": ingredient.QuantityRequired,
                    "menu_item_id": ingredient.MenuItemID
                })
        
        menu_items_serializable = [
            {
                "id": menu_item.MenuItemID,
                "name": menu_item.ItemName,
                "description": menu_item.Description,
                "price": menu_item.Price,
                "availability_status": menu_item.AvailabilityStatus,
                "quantity": next((item["Quantity"] for item in order_data if item["MenuItemID"] == menu_item.MenuItemID), None)
            }
            for menu_item in menu_items_data
        ]
        return jsonify({"menu_items": menu_items_serializable, "ingredients": detailed_ingredients}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        inventory_response = requests.post(f"{INVENTORY_SERVICE_URL}/inventory/batch", json={"ingredient_ids": list(ingredient_ids)})
        inventory_data = inventory_response.json() if inventory_response.status_code == 200 else {}

        # Check ingredient availability for each menu item
        result = []

        for item in menu_items: 
            is_available = True
            if item.MenuItemID in ingredients_dict:
                for ingredient in ingredients_dict[item.MenuItemID]:
                    available_quantity = inventory_data.get(str(ingredient.IngredientID), {}).get("quantity_available", 0)
                    
                    # Determine error type based on inventory data
                    error_type = None
                    issue = None  # Variable to store additional info about the issue
                    
                    ingredient_name = inventory_data.get(str(ingredient.IngredientID), {}).get("name", "Unknown Ingredient")
                    if str(ingredient.IngredientID) not in inventory_data:
                        error_type = 101  # Ingredient Not Found
                        issue = f"Ingredient: {ingredient_name} (ID: {ingredient.IngredientID}) not found in inventory data."
                    elif available_quantity < 0:
                        error_type = 102  # Ingredient Out of Stock
                        issue = f"Ingredient: {ingredient_name} (ID: {ingredient.IngredientID}) is out of stock."
                    elif inventory_data.get(str(ingredient.IngredientID), {}).get("expiry_date", False) and \
                         datetime.strptime(inventory_data[str(ingredient.IngredientID)]["expiry_date"], "%Y-%m-%d").date() < datetime.today().date():
                        error_type = 103  # Ingredient Expired
                        issue = f"Ingredient: {ingredient_name} (ID: {ingredient.IngredientID}) has expired."
                    elif available_quantity < ingredient.QuantityRequired:
                        error_type = 104  # Insufficient Quantity Available
                        issue = f"Ingredient: {ingredient_name} (ID: {ingredient.IngredientID}) has insufficient quantity. Required: {ingredient.QuantityRequired}, Available: {available_quantity}."
                    elif available_quantity < inventory_data.get(str(ingredient.IngredientID), {}).get("reorder_threshold", 0):
                        error_type = 105  # Reorder Threshold Reached
                        issue = f"Ingredient: {ingredient_name} (ID: {ingredient.IngredientID}) has reached reorder threshold. Available: {available_quantity}."
                
                    # Trigger error resolution service if an error type is identified
                    if error_type:
                        is_available = False
                        error_data = {
                            "ErrorType": error_type,
                            "AdditionalInfo": f"{issue} for Menu Item {item.MenuItemID}",
                        }
                        error_response = requests.post(f"{ERROR_RESOLUTION_URL}/error/trigger", json=error_data)
                        if error_response.status_code != 200:
                            print(f"Failed to trigger error resolution for item {item.MenuItemID} and ingredient {ingredient.IngredientID}")
                        # Log the error resolution attempt
                        print(f"Error resolution triggered for item {item.MenuItemID} and ingredient {ingredient.IngredientID}")
                    # Break out of the loop if any ingredient is unavailable
                    break

            # Update availability status based on ingredient check
            if not is_available:
                item.AvailabilityStatus = False
                print(f"Menu item {item.ItemName} availability status: {item.AvailabilityStatus}")
            # Append menu item details to the result list
            result.append({
                "id": item.MenuItemID,
                "name": item.ItemName,
                "description": item.Description,
                "price": item.Price,
                "availability_status": item.AvailabilityStatus
            })
        print(f"Menu items fetched successfully: {len(result)} items found.")
        # Return the result list as part of the response
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

    # try:
    #     itemIDs = [int(id.strip()) for id in itemIDs.split(",")]
    #     menu_items = Menu.query.filter(Menu.MenuItemID.in_(itemIDs)).all()
    #     result = []
    #     for item in menu_items:
    #         result.append({
    #             "id": item.MenuItemID,
    #             "name": item.ItemName,
    #             "description": item.Description,
    #             "price": item.Price,
    #             "availability_status": item.AvailabilityStatus
    #         })
    #     return jsonify(result), 200
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
