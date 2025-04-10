# ESD Kitchen Management

## Introduction


This project, `esd-kitchen-management`, is designed to streamline and manage kitchen operations efficiently. It includes features such as inventory management, order tracking, order creation and feedback aggregation.

## Features

- **Inventory Management**: Keep track of all ingredients and supplies.
- **View Menu**: Menu items will be shown based on availability of the ingredients needed to prepare the items. 

- **Error Resolution**: When the menu service determined that there is not enough ingredients to prepare the menu item, it will call the Error Resolution Service which will invoke the inventory service to restock the ingredients.
<!--  -->
- **Order Creation**: Users checkout the food items which will create an order job for the kitchen to prepare. 

- **Kitchen Station Management**: 
    - To keep track of all orders created and sent to the kitchen for preparations. 
    - Orders will be assigned to a station for preparation, and the chef at that station can view the items that they have to prepare. 
    - Upon accepting the task, the ingredients and quantity of the ingredients needed to prepare the items will be shown. This is so that the chef can easily reference it. 

- **Order Tracking**: After orders creation, users are able to view the status of their orders.  


<!-- GETTING STARTED -->

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


## Usage (with Docker)

<!-- To start the application, run:
```bash
docker compose up -d --build
```
or

```bash
docker compose up -d
``` -->
## For scenario 1
cd esd-kitchen-management
docker-compose -f compose.yaml up -d --build
## For scenario 2
cd esd-kitchen-management 
docker-compose -f compose_scenario2.yaml up -d --build
## For scenario 3
cd esd-kitchen-management/feedback_service
docker-compose -f compose.yaml up -d --build




## Technical Diagrams
## Built With

### Frontend

- HTML
- CSS
- JS


### Backend

- [Python](https://python.org/)
- [Outsystems](https://success.outsystems.com/documentation/)

### Message Brokers

- [RabbitMQ](https://rabbitmq.com)

### DevOps

- [Docker](https://docker.com)

### External APIs used


- [Stripe API](https://stripe.com/docs/api/payment_intents)
- [Mailjet SMTP](https://dev.mailjet.com/email/guides/)

<p align="right">(<a href="#top">back to top</a>)</p>

## Beyond the Labs

* External API
  - Stripe Payment API

<p align="right">(<a href="#top">back to top</a>)</p>
