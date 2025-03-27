import subprocess
import threading
import time
from pathlib import Path

# List of all services to run with their ports
SERVICES = [
    {"name": "Fresh Farms", "file": "supplier_freshfarms.py", "port": 5010},
    {"name": "Organic Goods", "file": "supplier_organicgoods.py", "port": 5011},
    {"name": "Dairy Delight", "file": "supplier_dairydelight.py", "port": 5012},
    {"name": "Cheese Haven", "file": "supplier_cheesehaven.py", "port": 5016},
    {"name": "Lettuce Land", "file": "supplier_lettuceland.py", "port": 5017},
    {"name": "Tomato Express", "file": "supplier_tomatoexpress.py", "port": 5018},
    {"name": "Restocking Service", "file": "restocking.py", "port": 5005},
    {"name": "Manage Inventory", "file": "manage_inventory.py", "port": 5006},
    {"name": "API Gateway", "file": "api_gateway.py", "port": 5007}
]

def run_service(service):
    """Run a service in a separate process"""
    try:
        print(f"🚀 Starting {service['name']} on port {service['port']}...")
        cmd = f"python {service['file']}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {service['name']}: {e}")

def start_rabbitmq():
    """Start RabbitMQ if not already running (Linux/Mac example)"""
    try:
        print("🐇 Checking RabbitMQ...")
        subprocess.run("rabbitmqctl status", shell=True, check=True)
        print("RabbitMQ is already running")
    except:
        print("Starting RabbitMQ...")
        subprocess.run("rabbitmq-server start", shell=True)

def main():
    # Verify all files exist
    missing_files = [s['file'] for s in SERVICES if not Path(s['file']).exists()]
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return

    # Start RabbitMQ (optional - uncomment if needed)
    # start_rabbitmq()

    # Start all services in separate threads
    threads = []
    for service in SERVICES:
        t = threading.Thread(target=run_service, args=(service,))
        t.start()
        threads.append(t)
        time.sleep(0.5)  # Small delay between starting services

    print("\n✅ All services started. Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")

if __name__ == "__main__":
    main()