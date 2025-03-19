from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
from os import environ

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://root@localhost:3306/restocking"
)
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
    Priority = db.Column(db.Integer, nullable=False)

# Endpoint to receive low stock alerts from inventory service
@app.route("/restock", methods=["POST"])
def restock():
    data = request.get_json()
    ingredient_name = data.get("ingredient_name")
    amount_needed = data.get("amount_needed")

    # Find the ingredient ID
    ingredient = db.session.scalar(db.select(Ingredient).filter_by(IngredientName=ingredient_name))
    if not ingredient:
        return jsonify({"code": 404, "message": "Ingredient not found."}), 404
    
    # Find suppliers in priority order
    supplier_relations = db.session.scalars(
        db.select(SupplierIngredient).filter_by(IngredientID=ingredient.IngredientID).order_by(SupplierIngredient.Priority.asc())
    ).all()
    
    if not supplier_relations:
        return jsonify({"code": 404, "message": "No suppliers available for this ingredient."}), 404
    
    #THIS SHOULD BE CHANGED
    supplier_service_url = "http://supplier-microservice/order"
    
    for supplier_relation in supplier_relations:
        supplier = db.session.get(Supplier, supplier_relation.SupplierID)
        
        # Prepare order data
        order_data = {
            "supplier_name": supplier.SupplierName,
            "ingredient_name": ingredient_name,
            "amount_needed": amount_needed
        }
        
        response = requests.post(supplier_service_url, json=order_data)
        
        if response.status_code == 200:
            return jsonify({"code": 200, "message": "Order placed successfully.", "data": order_data})
    
    return jsonify({"code": 500, "message": "All suppliers failed to fulfill the order."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)