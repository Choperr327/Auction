from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class AuctionItem(db.Model):
    __tablename__ = 'auction_item'  
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    current_bid = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    
    bids = db.relationship('Bid', backref='auction_item', lazy=True)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bidder_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('auction_item.id'), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign Key to User

    user = db.relationship('User', backref='bids')  

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        return str(self.id)
    
    # Метод для перевірки пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Метод для встановлення пароля
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)




