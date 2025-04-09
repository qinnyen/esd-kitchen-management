from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import pika
import json
import sys
import os

# ensure python can find the config file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATABASE_CONFIG

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure database connection (MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{DATABASE_CONFIG['feedback_db']['user']}:"
    f"{DATABASE_CONFIG['feedback_db']['password']}@"
    f"{DATABASE_CONFIG['feedback_db']['host']}:"
    f"{DATABASE_CONFIG['feedback_db']['port']}/"
    f"{DATABASE_CONFIG['feedback_db']['database']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define the Feedback model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.String(64), nullable=False)
    order_id = db.Column(db.String(64), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String(256))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)


# API Endpoints
@app.route('/')
def home():
    return 'Welcome to the Feedback Service!'

@app.route('/feedback', methods=['POST'])
def create_feedback():
    try:
        data = request.get_json()

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

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "Feedback Service is up!"})

# Scheduled task to check for low-rated items
def check_low_rated_items():
    with app.app_context():
        print("[Feedback Scheduler] Running scheduled task to check low-rated items...")

        feedbacks = Feedback.query.all()
        ratings_by_item = {}
        counts_by_item = {}

        for feedback in feedbacks:
            item_id = feedback.menu_item_id
            ratings_by_item[item_id] = ratings_by_item.get(item_id, 0) + feedback.rating
            counts_by_item[item_id] = counts_by_item.get(item_id, 0) + 1

        for item_id, total_rating in ratings_by_item.items():
            average_rating = total_rating / counts_by_item[item_id]
            if average_rating <= 2:
                menu_item_name = get_menu_item_name(item_id)

                if menu_item_name:
                    send_rabbitmq_alert(menu_item_name, average_rating)

def get_menu_item_name(item_id):
    try:
        import requests
        response = requests.get(f'http://menu-service:5002/menu/item/{item_id}')
        if response.status_code == 200:
            return response.json().get('name')
    except Exception as e:
        print(f"[Feedback Scheduler] Error fetching menu item name: {str(e)}")
    return None

def send_rabbitmq_alert(menu_item_name, average_rating):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
        channel = connection.channel()

        channel.queue_declare(queue='feedback_alert', durable=True)

        message = json.dumps({
            "menu_item_id": menu_item_name,
            "average_rating": average_rating
        })

        channel.basic_publish(exchange='',
                              routing_key='feedback_alert',
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # Make message persistent
                              ))
        print(f"[Feedback Scheduler] Sent message to RabbitMQ: {message}")
        connection.close()

    except Exception as e:
        print(f"[Feedback Scheduler] Error sending message to RabbitMQ: {e}")


# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_low_rated_items, trigger="interval", seconds=60)
scheduler.start()

# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003, debug=True)
