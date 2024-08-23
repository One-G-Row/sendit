from flask import Flask, session
from .config import db, bcrypt
""" from utils import generate_password_hash, check_password_hash"""
from sqlalchemy_serializer import SerializerMixin 


class Parcel(db.Model,SerializerMixin):
    __tablename__ = 'parcels'

    id = db.Column(db.Integer, primary_key=True)
    parcel_item = db.Column(db.String(100), nullable=False)
    parcel_description = db.Column(db.String(255), nullable=False)
    parcel_weight = db.Column(db.Float, nullable=False)
    parcel_cost = db.Column(db.Float, nullable=False)
    parcel_status = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    
    destination = db.relationship('Destination', back_populates='parcel')
    user = db.relationship('User', back_populates='parcels')
    myorder = db.relationship('MyOrder', back_populates='parcel')

class Destination(db.Model, SerializerMixin):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), unique=True, nullable=False)
    arrival_day = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    parcel = db.relationship('Parcel', back_populates='destination', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'arrival_day': self.arrival_day.isoformat() if self.arrival_day else None
        }

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    _password_hash = db.Column(db.String(255), nullable=False)
    parcels = db.relationship('Parcel', back_populates='user')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
            # Avoid adding 'parcels' here to prevent recursion
        }


class Admin(db.Model,SerializerMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class MyOrder(db.Model, SerializerMixin):
    __tablename__ = 'myorders'

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False)
    recipient_name = db.Column(db.String(50), nullable=True)
    recipient_contact = db.Column(db.Integer, nullable=False, default=0)

    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'), nullable=True)
    parcel = db.relationship('Parcel', back_populates='myorder')


