# ESD Kitchen Management

## Introduction

This project, `esd-kitchen-management`, is designed to streamline and manage kitchen operations efficiently. It includes features such as inventory management, order tracking, order creation etc <--- ==need to update==. 

## Features

- **Inventory Management**: Keep track of all ingredients and supplies.

- **View Menu**: Menu items will be shown based on availability of the ingredients needed to prepare the items. 

- **Error Resolution**: When the menu service determined that there is not enough ingredients to prepare the menu item, it will call the Error Resolution Service which will invoke the inventory service to restock the ingredients.

- **Order Creation**: Users checkout the food items which will create an order job for the kitchen to prepare. 

- **Kitchen Station Management**: 
    - To keep track of all orders created and sent to the kitchen for preparations. 
    - Orders will be assigned to a station for preparation, and the chef at that station can view the items that they have to prepare. 
    - Upon accepting the task, the ingredients and quantity of the ingredients needed to prepare the items will be shown. This is so that the chef can easily reference it. 

- **Order Tracking**: After orders creation, users are able to view the status of their orders.  

## Installation

To install the project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/qinnyen/esd-kitchen-management.git
    ```
2. Navigate to the project directory:
    ```bash
    cd esd-kitchen-management
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage (without Docker)

To start the application, run:
```bash
flask run
```
To start the services, navigate to the respective service folders and run:
```bash
# inventory service
cd inventory_service
python app.py
```

## Usage (with Docker)

To start the application, run:
```bash
docker compose up -d --build
```
or

```bash
docker compose up -d
```


## Technical Diagrams


## Tech Stacks
- Flask
- Python
- Outsystems
- HTML
- JS 
- CSS

### BTL
- Docker
- RabbitMQ 
- Stripe


## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License