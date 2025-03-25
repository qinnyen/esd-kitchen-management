from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE_CONFIG

# Initialize Flask app
app = Flask(__name__)

# Configure database connection (MySQL, consistent with your team)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['feedback_db']['user']}:{DATABASE_CONFIG['feedback_db']['password']}@{DATABASE_CONFIG['feedback_db']['host']}:{DATABASE_CONFIG['feedback_db']['port']}/{DATABASE_CONFIG['feedback_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define the Feedback model/table structure
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incremented ID
    menu_item_id = db.Column(db.String(64), nullable=False)  # ID of the menu item
    order_id = db.Column(db.String(64), nullable=False)  # ID of the order
    rating = db.Column(db.Integer, nullable=False)  # Customer's rating (1–5)
    tags = db.Column(db.String(256))  # Optional tags (stored as comma-separated string)
    description = db.Column(db.Text)  # Optional textual feedback
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Time of submission

# API endpoint to create new feedback
@app.route("/feedback", methods=["POST"])
def create_feedback():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["menu_item_id", "order_id", "rating"]
        missing = [field for field in required_fields if field not in data]

        if missing:
            return jsonify({
                "error": "Missing required field(s)",
                "missing_fields": missing
            }), 400

        if not (1 <= int(data["rating"]) <= 5):
            return jsonify({
                "error": "Rating must be between 1 and 5"
            }), 400

        # Create Feedback object
        new_feedback = Feedback(
            menu_item_id=data["menu_item_id"],
            order_id=data["order_id"],
            rating=data["rating"],
            tags=",".join(data.get("tags", [])),
            description=data.get("description", "")
        )

        db.session.add(new_feedback)
        db.session.commit()

        return jsonify({"message": "Feedback submitted successfully"}), 201

    except Exception as e:
        return jsonify({
            "error": "An error occurred while processing feedback",
            "details": str(e)
        }), 500


# Health check endpoint for Docker/monitoring
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Feedback Service is up!"})

# Run the Flask app (for local development)
if __name__ == "__main__":
    app.run(port=5003, debug=True)
