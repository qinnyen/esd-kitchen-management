DATABASE_CONFIG = {
    'menu_db': {
        'host': 'mysql_service',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_menu'
    },
    'order_fulfillment_db': {
        'host': 'mysql_service',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_order_fulfillment'
    },
    'inventory_db': {
        'host': 'mysql_service',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_inventory'
    },
    'kitchen_station_db': {
        'host': 'mysql_service',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_kitchen_station'
    },
    'restocking_db': {
        'host': 'mysql_service',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_restocking'
    },
    'feedback_db': {
        'host': 'localhost',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_feedback'
    },
    'orderdb': {
        'host': 'localhost',  # Replace with MySQL service name in docker-compose
        'port': 3306,
        'user': 'root',
        'password': '',  # Make sure this matches your MySQL root password
        'database': 'is213_order'
    }
}
