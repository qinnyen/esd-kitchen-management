from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def process_order():
    ingredient = request.json.get("ingredient_name")
    if ingredient in ["Tomato", "Lettuce"]:
        return jsonify({
            "status": "error",
            "message": "Fresh Farms: Forced failure for testing",
            "supplier": "Fresh Farms"
        })
    return jsonify({
        "status": "success",
        "message": "Order fulfilled by Fresh Farms",
        "supplier": "Fresh Farms"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=False)