from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
# sys.path.append('..')
from config import DATABASE_CONFIG  
# from models import db, KitchenStation
from datetime import datetime
import pika
import json

app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['kitchen_station_db']['user']}:{DATABASE_CONFIG['kitchen_station_db']['password']}@{DATABASE_CONFIG['kitchen_station_db']['host']}:{DATABASE_CONFIG['kitchen_station_db']['port']}/{DATABASE_CONFIG['kitchen_station_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
class KitchenStation(db.Model):
    __tablename__ = 'KitchenStation'
    TaskID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, nullable=False)
    StationID = db.Column(db.Integer, nullable=False)
    TaskStatus = db.Column(db.String(50), nullable=False)
    StartTime = db.Column(db.TIMESTAMP, nullable=True)
    EndTime = db.Column(db.TIMESTAMP, nullable=True)
@app.route('/kitchen/stations', methods=['GET'])
def get_tasks_by_station():
    try:
        # Query distinct StationIDs
        distinct_station_ids = db.session.query(KitchenStation.StationID).distinct().all()

        result = []
        for station_id_tuple in distinct_station_ids:
            station_id = station_id_tuple[0]
            
            # Fetch all tasks for the current StationID
            tasks = KitchenStation.query.filter_by(StationID=station_id).all()
            result.append({
                "station_id": station_id,
                "tasks": [
                    {
                        "task_id": task.TaskID,
                        "order_id": task.OrderID,
                        "task_status": task.TaskStatus,
                        "start_time": task.StartTime.strftime('%Y-%m-%d %H:%M:%S') if task.StartTime else None,
                        "end_time": task.EndTime.strftime('%Y-%m-%d %H:%M:%S') if task.EndTime else None
                    }
                    for task in tasks
                ]
            })

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kitchen/assign', methods=['POST'])
def assign_task():
    try:
        data = request.get_json()
        order_id = data["order_id"]
        station_id = data["station_id"]
        ingredients = data.get("ingredients", [])
        task_status = "Assigned"

        new_task = KitchenStation(
            OrderID=order_id,
            StationID=station_id,
            TaskStatus=task_status,
            StartTime=None,
            EndTime=None
        )
        db.session.add(new_task)
        db.session.commit()

        # Send RFID events to RabbitMQ for each ingredient used
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="host.docker.internal"))
            channel = connection.channel()
            channel.exchange_declare(exchange='rfid_exchange', exchange_type='direct', durable=True)

            for ingredient in ingredients:
                payload = {
                    "order_id": order_id,
                    "station_id": station_id,
                    "ingredient_id": ingredient["ingredient_id"],
                    "quantity_used": ingredient["quantity_used"]
                }
                channel.basic_publish(
                    exchange='rfid_exchange',
                    routing_key='rfid.scan',
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                print(f"[RFID Trigger] Sent ingredient scan for IngredientID {ingredient['ingredient_id']}",flush=True)

            connection.close()
        except Exception as e:
            print(f"[RFID Error] Failed to send RFID events: {str(e)}",flush=True)

        return jsonify({"message": "Task assigned successfully", "task_id": new_task.TaskID}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kitchen/status/<int:task_id>', methods=['GET'])
def get_task_status(task_id):
    try:
        task = KitchenStation.query.filter_by(TaskID=task_id).first()
        if task:
            result = {
                "task_id": task.TaskID,
                "order_id": task.OrderID,
                "station_id": task.StationID,
                "task_status": task.TaskStatus,
                "start_time": task.StartTime.strftime('%Y-%m-%d %H:%M:%S') if task.StartTime else None,
                "end_time": task.EndTime.strftime('%Y-%m-%d %H:%M:%S') if task.EndTime else None
            }
            return jsonify(result), 200
        else:
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kitchen/task/<int:task_id>', methods=['PUT'])
def update_task_progress(task_id):
    try:
        data = request.get_json()
        new_status = data["task_status"]

        # Fetch the task from the database
        task = KitchenStation.query.filter_by(TaskID=task_id).first()
        if task:
            # Update task status
            task.TaskStatus = new_status

            # Automatically set StartTime and EndTime based on status
            if new_status == "In Progress" and not task.StartTime:
                task.StartTime = datetime.now()  # Set current timestamp as StartTime
            elif new_status == "Completed" and not task.EndTime:
                task.EndTime = datetime.now()  # Set current timestamp as EndTime

            db.session.commit()
            return jsonify({"message": f"Task {task_id} updated to '{new_status}' successfully"}), 200
        else:
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008, debug=True)
