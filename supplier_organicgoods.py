from flask import Flask, request, jsonify
import time

app = Flask(__name__)

INVENTORY = {
    "Cheese": True,
    "Tomato": False
}

@app.route('/check_availability', methods=['GET'])
def check_availability():
    time.sleep(1.5)
    ingredient = request.args.get('ingredient_name')
    if ingredient not in INVENTORY:
        return jsonify({
            "available": False,
            "supplier": "Organic Goods",
            "reason": "Unsupported ingredient"
        })
    return jsonify({
        "available": INVENTORY[ingredient],
        "supplier": "Organic Goods",
        "reason": "In stock" if INVENTORY[ingredient] else "Out of stock",
    })

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    ingredient = data["ingredient_name"]
    
    if ingredient not in INVENTORY:
        return jsonify({
            "status": "error",
            "supplier": "Organic Goods",
            "message": "Unsupported ingredient"
        }), 400
    
    if not INVENTORY[ingredient]:
        return jsonify({
            "status": "error",
            "supplier": "Organic Goods",
            "message": f"Temporarily out of {ingredient}"
        }), 400
    
    return jsonify({
        "status": "success",
        "supplier": "Organic Goods",
        "ingredient": ingredient,
        "amount": data["amount"],
        "unit": data["unit"],
        "message": f"{data['amount']} {data['unit']} of {ingredient} confirmed"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=False)