from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Service URLs (replace localhost with container names in Docker later)
ORDER_SERVICE_URL = "http://localhost:5001/order"  # Order validation API
FEEDBACK_SERVICE_URL = "http://localhost:5003/feedback"  # Feedback storage API

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()

        # Step 1: Basic field validation
        required = ["menu_item_id", "order_id", "rating"]
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

        # Step 2: Validate order with Order Service
        try:
            order_response = requests.get(f"{ORDER_SERVICE_URL}/{data['order_id']}")
            if order_response.status_code != 200:
                return jsonify({
                    "error": "Invalid order ID or order not found"
                }), 404
        except Exception as e:
            return jsonify({
                "error": "Order Service unreachable",
                "details": str(e)
            }), 502

        # Step 3: Submit feedback to Feedback Service
        try:
            feedback_payload = {
                "menu_item_id": data["menu_item_id"],
                "order_id": data["order_id"],
                "rating": data["rating"],
                "tags": data.get("tags", []),
                "description": data.get("description", "")
            }

            fb_response = requests.post(FEEDBACK_SERVICE_URL, json=feedback_payload)

            if fb_response.status_code != 201:
                return jsonify({
                    "error": "Feedback Service failed",
                    "details": fb_response.json()
                }), 500

        except Exception as e:
            return jsonify({
                "error": "Feedback Service unreachable",
                "details": str(e)
            }), 502

        # All good
        return jsonify({"message": "Feedback submitted successfully"}), 201

    except Exception as e:
        return jsonify({
            "error": "Unexpected error in Submit Feedback Service",
            "details": str(e)
        }), 500

# Health check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Submit Feedback Service is running"})

if __name__ == "__main__":
    app.run(port=5005, debug=True)
