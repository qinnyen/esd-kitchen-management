1. start rabbitmq container and WAMP server

2. docker-compose up --build

3. create .env file in folder

Testing order_service (get using order_id)

    GET http://127.0.0.1:5001/order/100

Testing submit_feedback_service & feedback_service 
(submit feedback to feedback_service, menu_id & order_id must match to the one in order_db, feedback_service will save the record to db)
    
    POST http://127.0.0.1:5005/submit_feedback
    
    json:

        {
            "menu_item_id": 12345,
            "order_id": 101,
            "rating": 4,
            "tags": ["delicious", "spicy"],
            "description": "Great meal!"
        }
    
    will get repsonse 201

Testing aggregator
(collect all feedback record that the average rating is below 2 in db, send to amqp)

Tesing notification
(send SMTP email to the manager, check junk mail)