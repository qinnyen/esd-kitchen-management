from flask import Flask, request, jsonify
import time

app = Flask(__name__)

INVENTORY = {
    "Tomato": False
}

@app.route('/check_availability', methods=['GET'])
def check_availability():
    ingredient = request.args.get('ingredient_name')
    if ingredient not in INVENTORY:
        return jsonify({
            "available": False,
            "supplier": "Tomato Express",
            "reason": "Unsupported ingredient"
        })
    return jsonify({
        "available": INVENTORY[ingredient],
        "supplier": "Tomato Express",
        "reason": "In stock" if INVENTORY[ingredient] else "Out of stock"
    })

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    ingredient = data["ingredient_name"]
    
    if ingredient not in INVENTORY:
        return jsonify({
            "status": "error",
            "supplier": "Tomato Express",
            "message": "Unsupported ingredient"
        }), 400
    
    if not INVENTORY[ingredient]:
        return jsonify({
            "status": "error",
            "supplier": "Tomato Express",
            "message": f"Temporarily out of {ingredient}"
        }), 400
    
    return jsonify({
        "status": "success",
        "supplier": "Tomato Express",
        "ingredient": ingredient,
        "amount": data["amount"],
        "unit": data["unit"],
        "message": f"{data['amount']} {data['unit']} of {ingredient} confirmed"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5019, debug=False)