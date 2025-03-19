CREATE DATABASE is214_order_fulfillment;
use is214_order_fulfillment;
CREATE TABLE OrderFulfillment (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    MenuItemIDs VARCHAR(255) NOT NULL,
    TotalPrice FLOAT NOT NULL,
    OrderStatus VARCHAR(50) NOT NULL,
    AssignedStationID INT DEFAULT NULL,
    NotificationSent BOOLEAN DEFAULT FALSE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);