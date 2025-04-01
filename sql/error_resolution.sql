CREATE TABLE ErrorResolution (
    ErrorID INT PRIMARY KEY AUTO_INCREMENT,
    ErrorType INT NOT NULL,
    ResolutionStatus VARCHAR(50) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    ResolvedAt DATETIME NULL
);

CREATE TABLE ErrorLogs (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    ErrorID INT NOT NULL,
    OccurredAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    AdditionalInfo TEXT,
    FOREIGN KEY (ErrorID) REFERENCES ErrorResolution(ErrorID)
);

