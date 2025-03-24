from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    if random.random() < 0.8:  # 80% success rate
        return jsonify({
            "status": "success",
            "supplier": "Tomato Express",
            "order_id": request.json.get("order_id"),
            "message": "Order shipped"
        })
    return jsonify({
        "status": "error",
        "supplier": "Tomato Express",
        "message": "Transportation issue"
    })

@app.route('/cancel', methods=['POST'])
def cancel_order():
    return jsonify({"status": "canceled"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5018, debug=False)