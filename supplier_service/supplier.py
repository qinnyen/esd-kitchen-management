from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/restocking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Supplier(db.Model):
    __tablename__ = 'Suppliers'

    SupplierID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SupplierName = db.Column(db.String(255), nullable=False)
    Address = db.Column(db.String(255), nullable=True)
    ContactInfo = db.Column(db.String(255), nullable=True)

    def json(self):
        return {
            "SupplierID": self.SupplierID,
            "SupplierName": self.SupplierName,
            "Address": self.Address,
            "ContactInfo": self.ContactInfo
        }

class Ingredient(db.Model):
    __tablename__ = 'Ingredients'

    IngredientID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IngredientName = db.Column(db.String(255), nullable=False)

    def json(self):
        return {
            "IngredientID": self.IngredientID,
            "IngredientName": self.IngredientName
        }

class SupplierIngredient(db.Model):
    __tablename__ = 'SupplierIngredient'

    IngredientID = db.Column(db.Integer, db.ForeignKey('Ingredients.IngredientID'), primary_key=True)
    SupplierID = db.Column(db.Integer, db.ForeignKey('Suppliers.SupplierID'), primary_key=True)
    Priority = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            "IngredientID": self.IngredientID,
            "SupplierID": self.SupplierID,
            "Priority": self.Priority
        }

@app.route("/suppliers", methods=['GET'])
def get_all_suppliers():
    suppliers = db.session.scalars(db.select(Supplier)).all()
    if suppliers:
        return jsonify({"code": 200, "data": [s.json() for s in suppliers]})
    return jsonify({"code": 404, "message": "No suppliers found."}), 404

@app.route("/order", methods=['POST'])
def place_order():
    data = request.get_json()
    
    if not data or 'IngredientID' not in data or 'Quantity' not in data:
        return jsonify({"code": 400, "message": "Missing required fields: IngredientID and Quantity."}), 400
    
    # Find suppliers for the requested ingredient ordered by priority
    suppliers = db.session.scalars(
        db.select(SupplierIngredient).filter_by(IngredientID=data['IngredientID']).order_by(SupplierIngredient.Priority)
    ).all()
    
    if not suppliers:
        return jsonify({"code": 404, "message": "No suppliers found for the requested ingredient."}), 404

    # Select the highest priority supplier
    selected_supplier = db.session.get(Supplier, suppliers[0].SupplierID)
    
    if data["IngredientID"] == 3:
       return jsonify({
        "code": 404,
        "message": "Order is NOT placed successfully.",
        "supplier": selected_supplier.json(),
        "IngredientID": data['IngredientID'],
        "Quantity": data['Quantity']
        }), 404
    
    return jsonify({
        "code": 201,
        "message": "Order placed successfully.",
        "supplier": selected_supplier.json(),
        "IngredientID": data['IngredientID'],
        "Quantity": data['Quantity']
    }), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006, debug=True)
