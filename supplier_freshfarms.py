from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    # Simulate random success (70% chance)
    if random.random() < 0.7:
        return jsonify({
            "status": "success",
            "message": "Order fulfilled by Fresh Farms",
            "supplier": "Fresh Farms",
            "order_data": request.json
        })
    return jsonify({
        "status": "error",
        "message": "Fresh Farms cannot fulfill order",
        "order_data": request.json
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=False)