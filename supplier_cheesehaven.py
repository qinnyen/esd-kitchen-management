from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    if random.random() < 0.7:  # 70% success rate
        return jsonify({
            "status": "success",
            "supplier": "Cheese Haven",
            "order_id": request.json.get("order_id"),
            "message": "Order fulfilled"
        })
    return jsonify({
        "status": "error",
        "supplier": "Cheese Haven",
        "message": "Out of stock"
    })

@app.route('/cancel', methods=['POST'])
def cancel_order():
    print(f"Cancelled order {request.json.get('order_id')}")
    return jsonify({"status": "canceled"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5016, debug=False)