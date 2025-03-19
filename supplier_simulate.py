from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/simulate_order', methods=['POST'])
def simulate_order():
    """Simulate an order with an external supplier and return a success/failure response."""
    order_data = request.get_json()
    print(f" [Supplier Simulation Service] Simulating order: {order_data}")

    ingredient_name = order_data["ingredient_name"]
    supplier_name = order_data["supplier_name"]

    # Simulate success/failure based on supplier and ingredient
    if ingredient_name == "Tomato":
        if supplier_name == "Fresh Farms":  # Priority 1
            return jsonify({
                "status": "error",
                "message": f"Failed to place order with {supplier_name}.",
                "order_data": order_data
            })
        elif supplier_name == "Organic Goods":  # Priority 2
            return jsonify({
                "status": "success",
                "message": f"Order for {order_data['amount_needed']} units of {ingredient_name} placed successfully with {supplier_name}.",
                "order_data": order_data
            })
    elif ingredient_name == "Cheese":
        if supplier_name == "Dairy Delight":  # Priority 1
            return jsonify({
                "status": "error",
                "message": f"Failed to place order with {supplier_name}.",
                "order_data": order_data
            })
    elif ingredient_name == "Lettuce":
        if supplier_name == "Fresh Farms":  # Priority 1
            return jsonify({
                "status": "success",
                "message": f"Order for {order_data['amount_needed']} units of {ingredient_name} placed successfully with {supplier_name}.",
                "order_data": order_data
            })

    # Default response for unknown ingredients/suppliers
    return jsonify({
        "status": "error",
        "message": "Unknown ingredient or supplier.",
        "order_data": order_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)