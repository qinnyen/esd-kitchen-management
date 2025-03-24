from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    """Simulate order processing with random success/failure and realistic delay"""
    order_data = request.json
    
    # Simulate processing delay (0.5-2 seconds)
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)
    
    # Simulate 80% success rate (adjust as needed)
    if random.random() < 0.8:
        return jsonify({
            "status": "success",
            "message": f"Order for {order_data['amount_needed']} units of {order_data['ingredient_name']} fulfilled by Organic Goods",
            "supplier": "Organic Goods",
            "processing_time": f"{processing_time:.2f}s",
            "order_data": order_data
        })
    
    # Simulated failure cases
    failure_reasons = [
        "Insufficient stock",
        "Shipping delay",
        "Quality check failed"
    ]
    return jsonify({
        "status": "error",
        "message": f"Organic Goods could not fulfill order: {random.choice(failure_reasons)}",
        "supplier": "Organic Goods",
        "order_data": order_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=False)