from flask import Flask, jsonify, render_template
import requests
app = Flask(__name__)

# Sample menu data
menu_items = [
    {"id": 1, "name": "Margherita Pizza", "description": "Classic cheese and tomato pizza", "price": 10.00},
    {"id": 2, "name": "Pepperoni Pizza", "description": "Pepperoni and cheese pizza", "price": 12.50},
    {"id": 3, "name": "Veggie Salad", "description": "Fresh garden vegetables with dressing", "price": 8.00},
    {"id": 4, "name": "Spaghetti Bolognese", "description": "Pasta with rich meat sauce", "price": 15.00},
    {"id": 5, "name": "Garlic Bread", "description": "Toasted bread with garlic butter", "price": 5.00},
]

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_MICROSERVICE_URL = "http://localhost:5002/menu/all"
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu/all', methods=['GET'])
def fetch_menu():
    try:
        response = requests.get(MENU_MICROSERVICE_URL)
        response.raise_for_status()
        menu_items = response.json()
        return jsonify(menu_items)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cart')
def cart():
    return render_template('cart.html')




if __name__ == "__main__":
    app.run(debug=True)
