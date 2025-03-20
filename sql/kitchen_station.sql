CREATE TABLE KitchenStation (
    TaskID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL,
    StationID INT NOT NULL,
    TaskStatus VARCHAR(50) NOT NULL,
    StartTime TIMESTAMP NULL,
    EndTime TIMESTAMP NULL
);
INSERT INTO KitchenStation (OrderID, StationID, TaskStatus, StartTime, EndTime)
VALUES 
(1, 101, 'Assigned', NULL, NULL),
(2, 102, 'In Progress', '2025-03-20 12:00:00', NULL),
(3, 103, 'Completed', '2025-03-20 11:00:00', '2025-03-20 12:30:00');