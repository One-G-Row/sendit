
from config import db, Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_serializer import SerializerMixin
from config import app, db, bcrypt


class Parcel(db.Model):
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

    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'arrival_day': self.arrival_day
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
        self._password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self._password_hash, password)

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
