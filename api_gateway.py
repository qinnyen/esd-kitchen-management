from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

app = Flask(__name__)

SUPPLIER_URLS = {
    "Cheese Haven": "http://localhost:5016",
    "Organic Goods": "http://localhost:5011",
    "Dairy Delight": "http://localhost:5012",
    "Lettuce Land": "http://localhost:5017",
    "Fresh Farms": "http://localhost:5010",
    "Tomato Express": "http://localhost:5018"
}

@app.route('/check_availability', methods=['POST'])
def check_availability():
    data = request.json
    ingredient_name = data["ingredient_name"]
    suppliers_to_check = data.get("suppliers", [])
    
    available_suppliers = []
    with ThreadPoolExecutor() as executor:
        future_to_supplier = {
            executor.submit(
                requests.get,
                f"{SUPPLIER_URLS[supplier]}/check_availability",
                params={"ingredient_name": ingredient_name},  # Critical fix
                timeout=2
            ): supplier for supplier in suppliers_to_check
        }
        
        for future in as_completed(future_to_supplier, timeout=3):
            supplier = future_to_supplier[future]
            try:
                if future.result().json().get("available"):
                    available_suppliers.append(supplier)
            except:
                continue
    
    return jsonify({
        "available_suppliers": available_suppliers,
        "ingredient": ingredient_name  # Added for traceability
    })

@app.route('/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    supplier = order_data["supplier_name"]
    
    try:
        response = requests.post(
            f"{SUPPLIER_URLS[supplier]}/place_order",
            json=order_data,
            timeout=5
        )
        # Mirror supplier response exactly
        result = response.json()
        result["gateway_status"] = "processed"  # Additional metadata
        return jsonify(result)
    
    except requests.exceptions.Timeout:
        return jsonify({
            "status": "error",
            "supplier": supplier,
            "ingredient": order_data.get("ingredient_name"),
            "message": "Supplier timeout"
        }), 504
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "supplier": supplier,
            "ingredient": order_data.get("ingredient_name"),
            "message": f"Gateway error: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=False)