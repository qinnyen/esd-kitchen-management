from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Service URLs
FEEDBACK_SERVICE_URL = "http://host.docker.internal:5003/feedback"

# Future-ready: Outsystems API endpoint
OUTSYSTEMS_URL_BASE = "https://personal-qptpra8g.outsystemscloud.com/Order/rest/v1"

HEADERS = {
    'Content-Type': 'application/json',
    'User-ID': '10'
}

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()

        # Step 1: Basic field validation
        required = ["menu_item_id", "menu_item_name", "order_id", "rating"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                "error": "Missing required field(s)",
                "missing_fields": missing
            }), 400

        if not (1 <= int(data["rating"]) <= 5):
            return jsonify({
                "error": "Rating must be between 1 and 5"
            }), 400

        # Step 2: Forward payload to Feedback Service
        try:
            feedback_payload = {
                "menu_item_id": data["menu_item_id"],
                "menu_item_name": data["menu_item_name"],
                "order_id": data["order_id"],
                "rating": data["rating"],
                "tags": data.get("tags", []),
                "description": data.get("description", "")
            }

            fb_response = requests.post(FEEDBACK_SERVICE_URL, json=feedback_payload, timeout=5)
            fb_response.raise_for_status()

        except requests.RequestException as e:
            return jsonify({
                "error": "Feedback Service unreachable",
                "details": str(e)
            }), 502

        return jsonify({
            "message": "Feedback submitted successfully",
            "order_id": data.get("order_id"),
            "menu_item_id": data.get("menu_item_id"),
            "menu_item_name": data.get("menu_item_name"),
            "rating": data.get("rating"),
            "tags": data.get("tags"),
            "description": data.get("description")
        }), 201

    except Exception as e:
        return jsonify({
            "error": "Unexpected error in Submit Feedback Service",
            "details": str(e)
        }), 500

@app.route("/get_order_details/<int:customerID>", methods=["GET"])
def get_order_details(customerID):
    if not customerID:
        return jsonify({"error": "Missing customerID"}), 400

    outsystems_url = f"{OUTSYSTEMS_URL_BASE}/OrdersByCustomerID/{customerID}"
    try:
        response = requests.get(outsystems_url, headers=HEADERS)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code

    except requests.HTTPError as http_err:
        return jsonify({"error": str(http_err), "details": response.text}), response.status_code

    except requests.RequestException as req_err:
        return jsonify({"error": "Request to Outsystems API failed", "details": str(req_err)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Submit Feedback Service is running"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005, debug=True)
