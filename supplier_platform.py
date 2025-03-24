from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import uuid

app = Flask(__name__)

SUPPLIER_SERVICES = {
    "Fresh Farms": "http://localhost:5010",
    "Organic Goods": "http://localhost:5011",
    "Dairy Delight": "http://localhost:5012",
    "Cheese Haven": "http://localhost:5016",
    "Lettuce Land": "http://localhost:5017",
    "Tomato Express": "http://localhost:5018"
}

def try_supplier(url, order_data):
    try:
        response = requests.post(f"{url}/order", json=order_data, timeout=2)
        return response.json() if response.ok else None
    except:
        return None

def cancel_supplier(url, order_data):
    try:
        requests.post(f"{url}/cancel", json=order_data, timeout=1)
    except:
        pass  # Silent fail for cancellations

@app.route('/place_order', methods=['POST'])
def place_order():
    order_data = request.json
    order_id = str(uuid.uuid4())
    enhanced_data = {**order_data, "order_id": order_id}
    
    attempted_suppliers = []
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(try_supplier, SUPPLIER_SERVICES[s["name"]], enhanced_data): s
            for s in order_data["suppliers"]
            if s["name"] in SUPPLIER_SERVICES
        }
        
        for future in as_completed(futures, timeout=5):
            supplier_name = futures[future]["name"]
            attempted_suppliers.append(supplier_name)
            result = future.result()
            if result and result.get("status") == "success":
                for other_future, supplier in futures.items():
                    if not other_future.done():
                        cancel_supplier(SUPPLIER_SERVICES[supplier["name"]], enhanced_data)
                return jsonify(result)
    
    return jsonify({
        "status": "error",
        "message": "All suppliers failed",
        "attempted_suppliers": attempted_suppliers,
        "order_id": order_id
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=False)