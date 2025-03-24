from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    return jsonify({
        "status": "error",
        "message": "Dairy Delight: Out of stock",
        "supplier": "Dairy Delight"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False)