from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    return jsonify({
        "status": "error",
        "message": "Tomato Express: Forced failure for testing",
        "supplier": "Tomato Express"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5018, debug=False)