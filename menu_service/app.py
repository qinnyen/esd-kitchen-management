from flask import Flask, jsonify

app = Flask(__name__)

# Sample menu data
menu_items = [
    {"id": 1, "name": "Margherita Pizza", "description": "Classic cheese and tomato pizza", "price": 10.00},
    {"id": 2, "name": "Pepperoni Pizza", "description": "Pepperoni and cheese pizza", "price": 12.50},
    {"id": 3, "name": "Veggie Salad", "description": "Fresh garden vegetables with dressing", "price": 8.00},
    {"id": 4, "name": "Spaghetti Bolognese", "description": "Pasta with rich meat sauce", "price": 15.00},
    {"id": 5, "name": "Garlic Bread", "description": "Toasted bread with garlic butter", "price": 5.00},
]

@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(menu_items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
