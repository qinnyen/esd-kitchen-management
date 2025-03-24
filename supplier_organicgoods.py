from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    ingredient = request.json.get("ingredient_name")
    if ingredient == "Tomato":
        return jsonify({
            "status": "error",
            "message": "Organic Goods: Tomato crop failure",
            "supplier": "Organic Goods"
        })
    # Simulate random delay (0.5-2s) for Lettuce/Cheese race condition
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return jsonify({
        "status": "success",
        "supplier": "Organic Goods",
        "processing_time": f"{delay:.2f}s"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=False)