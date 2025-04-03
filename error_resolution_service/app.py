from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys
import os
import requests
# sys.path.append('..')
from config import DATABASE_CONFIG
app = Flask(__name__)
# Configure Menu Service database
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DATABASE_CONFIG['error_resolution_db']['user']}:{DATABASE_CONFIG['error_resolution_db']['password']}@{DATABASE_CONFIG['error_resolution_db']['host']}:{DATABASE_CONFIG['error_resolution_db']['port']}/{DATABASE_CONFIG['error_resolution_db']['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://host.docker.internal:5004")  # Inventory Service URL for REST API calls
db = SQLAlchemy(app)

# Define ErrorResolution model
class ErrorResolution(db.Model):
    __tablename__ = 'ErrorResolution'
    ErrorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ErrorType = db.Column(db.Integer, nullable=False)
    ResolutionStatus = db.Column(db.String(50), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    ResolvedAt = db.Column(db.DateTime, nullable=True)

# Define ErrorLogs model
class ErrorLogs(db.Model):
    __tablename__ = 'ErrorLogs'
    LogID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ErrorID = db.Column(db.Integer, db.ForeignKey('ErrorResolution.ErrorID'), nullable=False)
    OccurredAt = db.Column(db.DateTime, default=datetime.utcnow)
    AdditionalInfo = db.Column(db.Text)

# Endpoint: Trigger an error (POST /error/trigger)
@app.route('/error/trigger', methods=['POST'])
def trigger_error():
    try:
        data = request.get_json()
        error_type = data['ErrorType']
        additional_info = data.get('AdditionalInfo', '')

        # Check if an unresolved error of the same type and additional info already exists
        unresolved_error = ErrorResolution.query.join(ErrorLogs).filter(
            ErrorResolution.ErrorType == error_type,
            ErrorResolution.ResolutionStatus == 'Pending',
            ErrorLogs.AdditionalInfo.like(f"%{additional_info}%")
        ).first()
        print(unresolved_error)
        if unresolved_error:
            return jsonify({
                "message": "Error already logged and not resolved",
                "ErrorID": unresolved_error.ErrorID
            }), 200
        
        # Create a new error resolution entry
        new_error = ErrorResolution(
            ErrorType=error_type,
            ResolutionStatus='Pending',
            CreatedAt=datetime.utcnow()
        )
        db.session.add(new_error)
        db.session.commit()

        # Create a new error log entry
        new_log = ErrorLogs(
            ErrorID=new_error.ErrorID,
            OccurredAt=datetime.utcnow(),
            AdditionalInfo=additional_info
        )
        db.session.add(new_log)
        db.session.commit()
        
        # Extract ingredient name from additional info
        if "Ingredient:" in additional_info and "(" in additional_info:
            ingredient_name = additional_info.split("Ingredient:")[1].split("(")[0].strip()
        else:
            ingredient_name = "unknown"

        # Call inventory service to restock the ingredient
        inventory_response = requests.post(
            f"{INVENTORY_SERVICE_URL}/inventory/restock",
            json={"ingredient_name": ingredient_name, "amount_needed": 20, "unit_of_measure": "kg"}
        )
        if  inventory_response.status_code != 200:
            return jsonify({"error": "Failed to notify inventory service"}), 500
        print(f" [Error Resolution Service] Sent to inventory service: {ingredient_name}")
        return jsonify({"message": "Error triggered successfully", "ErrorID": new_error.ErrorID}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint: Post an error (POST /error)
@app.route('/error', methods=['POST'])
def post_error():
    try:
        data = request.get_json()
        error_type = data['ErrorType']
        resolution_status = data['ResolutionStatus']
        resolved_at = data.get('ResolvedAt')

        # Create a new error resolution entry
        new_error = ErrorResolution(
            ErrorType=error_type,
            ResolutionStatus=resolution_status,
            CreatedAt=datetime.utcnow(),
            ResolvedAt=datetime.strptime(resolved_at, '%Y-%m-%d %H:%M:%S') if resolved_at else None
        )
        db.session.add(new_error)
        db.session.commit()

        return jsonify({"message": "Error posted successfully", "ErrorID": new_error.ErrorID}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Get all error logs (GET /error/logs)
@app.route('/error/logs', methods=['GET'])
def get_error_logs():
    try:
        logs = ErrorLogs.query.all()
        result = [
            {
                "LogID": log.LogID,
                "ErrorID": log.ErrorID,
                "OccurredAt": log.OccurredAt.strftime('%Y-%m-%d %H:%M:%S'),
                "AdditionalInfo": log.AdditionalInfo
            }
            for log in logs
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Get error details (GET /error/<int:error_id>)
@app.route('/error/<int:error_id>', methods=['GET'])
def get_error_details(error_id):
    try:
        error = ErrorResolution.query.filter_by(ErrorID=error_id).first()
        if not error:
            return jsonify({"error": f"Error with ID {error_id} not found"}), 404

        result = {
            "ErrorID": error.ErrorID,
            "ErrorType": error.ErrorType,
            "ResolutionStatus": error.ResolutionStatus,
            "CreatedAt": error.CreatedAt.strftime('%Y-%m-%d %H:%M:%S'),
            "ResolvedAt": error.ResolvedAt.strftime('%Y-%m-%d %H:%M:%S') if error.ResolvedAt else None
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013, debug=True)
