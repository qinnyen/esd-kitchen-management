from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    # Fast response (0.3s delay)
    time.sleep(0.3)
    return jsonify({
        "status": "success",
        "message": "Order fulfilled by Lettuce Land",
        "supplier": "Lettuce Land"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5017, debug=False)