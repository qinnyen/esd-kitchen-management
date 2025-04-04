import os

DATABASE_CONFIG = {
    'feedback_db': {
        'host': os.getenv('FEEDBACK_DB_HOST', 'host.docker.internal'),  # Use 'mysql' service name in Docker
        'port': int(os.getenv('FEEDBACK_DB_PORT', 3306)),
        'user': os.getenv('FEEDBACK_DB_USER', 'root'),
        'password': os.getenv('FEEDBACK_DB_PASSWORD', ''),
        'database': os.getenv('FEEDBACK_DB_NAME', 'is213_feedback')
    },
    'order_db': {
        'host': os.getenv('ORDER_DB_HOST', 'host.docker.internal'),
        'port': int(os.getenv('ORDER_DB_PORT', 3306)),
        'user': os.getenv('ORDER_DB_USER', 'root'),
        'password': os.getenv('ORDER_DB_PASSWORD', ''),
        'database': os.getenv('ORDER_DB_NAME', 'is213_order')
    }
}