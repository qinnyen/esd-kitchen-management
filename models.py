from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Menu Service Models
class Menu(db.Model):
    __bind_key__ = 'menu_db'
    __tablename__ = 'Menu'
    MenuItemID = db.Column(db.Integer, primary_key=True)
    ItemName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    Price = db.Column(db.Float, nullable=False)
    AvailabilityStatus = db.Column(db.Boolean, default=True)

class MenuIngredient(db.Model):
    __bind_key__ = 'menu_db'
    __tablename__ = 'MenuIngredient'
    MenuItemID = db.Column(db.Integer, nullable=False)
    IngredientID = db.Column(db.Integer, nullable=False)
    QuantityRequired = db.Column(db.Float, nullable=False)
    __table_args__ = (db.PrimaryKeyConstraint('MenuItemID', 'IngredientID'),)

# Order Fulfillment Service Models
class OrderFulfillment(db.Model):
    __bind_key__ = 'order_fulfillment_db'
    __tablename__ = 'OrderFulfillment'
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CustomerID = db.Column(db.Integer, nullable=False)
    MenuItemIDs = db.Column(db.String(255), nullable=False)
    TotalPrice = db.Column(db.Float, nullable=False)
    OrderStatus = db.Column(db.String(50), nullable=False)

# Inventory Service Models
class Inventory(db.Model):
    __bind_key__ = 'inventory_db'
    __tablename__ = 'Inventory'
    IngredientID = db.Column(db.Integer, primary_key=True)
    IngredientName = db.Column(db.String(100), nullable=False)
    QuantityAvailable = db.Column(db.Integer, nullable=False)
    UnitOfMeasure = db.Column(db.String(50), nullable=False)
    ExpiryDate = db.Column(db.Date, nullable=False)
