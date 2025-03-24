from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    return jsonify({
        "status": "success",
        "message": "Order fulfilled by Cheese Haven",
        "supplier": "Cheese Haven"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5016, debug=False)