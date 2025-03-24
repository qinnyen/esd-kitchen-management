from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    if random.random() < 0.5:  # 50% success rate
        return jsonify({
            "status": "success",
            "supplier": "Lettuce Land",
            "order_id": request.json.get("order_id"),
            "message": "Order fulfilled"
        })
    return jsonify({
        "status": "error",
        "supplier": "Lettuce Land",
        "message": "Harvest delayed"
    })

@app.route('/cancel', methods=['POST'])
def cancel_order():
    return jsonify({"status": "canceled"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5017, debug=False)