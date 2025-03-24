from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    ingredient = request.json.get("ingredient_name")
    
    # Force failures for specific ingredients
    if ingredient == "Tomato":
        return jsonify({
            "status": "error",
            "message": "Organic Goods: Tomato crop failure",
            "supplier": "Organic Goods"
        })
    elif ingredient == "Lettuce":
        return jsonify({
            "status": "error",
            "message": "Organic Goods: Lettuce out of season",
            "supplier": "Organic Goods"
        })
    
    # Success for Cheese (with random delay)
    delay = random.uniform(1.0, 3.0)  # Simulate slower response
    time.sleep(delay)
    return jsonify({
        "status": "success",
        "supplier": "Organic Goods",
        "processing_time": f"{delay:.2f}s",
        "message": f"Order for {ingredient} fulfilled"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=False)