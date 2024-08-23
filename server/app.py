from flask import Flask, jsonify, request, make_response, session
from flask_restful import Resource
from .models import Destination, User, Parcel, Admin, MyOrder 
from config import db, api, app
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import  create_access_token, jwt_required, get_jwt_identity

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None

class Signup(Resource):
    def get(self):
        return {}, 200
    
    def post(self):
        data = request.get_json()
        if not data:
            return {'error': 'No data provided'}, 400
        try:
            hashed_password = generate_password_hash(data['password'])
            user = User(
                first_name = data['first_name'],
                last_name = data['last_name'],
                email = data['email'],
                password = hashed_password
            )
            db.session.add(user)
            db.session.commit()
            return make_response(jsonify(user.to_dict()), 201)
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return {'error': str(e)}, 400

class CheckSession(Resource):
    def get(self):
        user = User.query.filter_by(id=session.get('user_id')).first()
        if user:
            response = jsonify(user.to_dict), 200
            return response
        else:
            return {}, 204
        
class LoginUser(Resource):
    def post(self):
        user = User.query.filter(User.email == request.get_json()['email']).first()
        if user:
            session['user_id'] = user.id
            response = make_response(jsonify(user.to_dict()), 200)
            return response 
        else:
            return {}, 401
           
class LoginAdmin(Resource):
    def post(self):
        data = request.get_json()
        admin = Admin.query.filter(Admin.email == data['email']).first()
        if admin and check_password_hash(admin.password_hash, data['password']):
            session['admin_id'] = admin.id
            response = make_response(jsonify(admin.to_dict()), 200)
            return response
        else:
            return {}, 401
        
class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204
        
# Define User-related endpoints
class Users(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return make_response(jsonify(user.to_dict()), 200)
        return make_response(jsonify({'error': 'User not found'}), 404)
    
    def patch(self, user_id):
        data = request.get_json()
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify(user.to_dict()), 200)
    
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'error': 'User not found'}), 404)
        
        db.session.delete(user)
        db.session.commit()
        return {}, 204

class UserList(Resource):
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return make_response(jsonify(users), 200)
    
    def post(self):
        data = request.get_json()
        if not data:
            return {'error': 'No data provided'}, 400
        try:
           if 'password' not in data:
               return {'error': 'Password is required'}, 400

           hashed_password = generate_password_hash(data['password'])
           user = User(
              first_name = data['first_name'],
              last_name = data['last_name'],
              email = data['email'],
              password = hashed_password
           )
           db.session.add(user)
           db.session.commit() 
           return make_response(jsonify(user.to_dict(), 201))
        
        except Exception as e:
           print("Error:", e) 
           db.session.rollback()
           return {'error': str(e)}, 400
    
class MyOrders(Resource):
    def get(self, myorder_id):
        myorder = MyOrder.query.get(myorder_id)
        if not myorder:
            return make_response(jsonify({'error': 'MyOrder not found'}), 404)
        return make_response(jsonify(myorder.to_dict()), 200)
    
    def delete(self, myorder_id):
        myorder = MyOrder.query.get(myorder_id)
        db.session.delete(myorder)
        db.session.commit()
        return '', 204


    def post(self):
        data = request.get_json()

        # Validate the incoming data
        required_fields = ['item', 'description', 'weight', 'destination', 'status', 'recipient_name', 'recipient_contact']
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({'error': f'Missing {field}'}), 400)

        # Create a new MyOrder object
        new_order = MyOrder(
            item=data['item'],
            description=data['description'],
            weight=data['weight'],
            destination=data['destination'],
            status=data['status'],
            recipient_name=data['recipient_name'],
            recipient_contact=data['recipient_contact'],
            cost=self.calculate_cost(data['destination'], data['weight'])  
        )
        # Add and commit the new order to the database
        try:
            db.session.add(new_order)
            db.session.commit()
            return make_response(jsonify(new_order.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            print("Error:", e)
            return {'error': str(e)}, 400
        
    def patch(self, myorder_id):
        data = request.get_json()
        myorder = MyOrder.query.get(myorder_id)
        if not myorder:
            return make_response(jsonify({'error': 'MyOrder not found'}), 404)
        
        # Update the order with the provided data
        if 'item' in data:
            myorder.item = data['item']
        if 'description' in data:
            myorder.description = data['description']
        if 'weight' in data:
            myorder.weight = data['weight']
        if 'destination' in data:
            myorder.destination = data['destination']
            myorder.cost = self.calculate_cost(data['destination'], myorder.weight)
        if 'cost' in data:
            myorder.cost = data['cost']
        if 'status' in data:
            myorder.status = data['status']
        if 'recipient_name' in data:
            myorder.recipient_name = data['recipient_name']
        if 'recipient_contact' in data:
            myorder.recipient_contact = data['recipient_contact']

 
        # Commit the updated order to the database
        db.session.add(myorder)
        db.session.commit()
        
        return make_response(jsonify(myorder.to_dict()), 200)

    def calculate_cost(self, destination, weight):
        base_cost = 10
        cost_per_kg = 2
        destination_multiplier = self.get_destination_multiplier(destination)
        return base_cost + (weight * cost_per_kg * destination_multiplier)
    
    def get_destination_multiplier(self, destination):
        return 1.5
        
class MyOrdersList(Resource):
    def get(self):
        myorders = [myorder.to_dict() for myorder in MyOrder.query.all()]
        return make_response(jsonify(myorders), 200)
    
    def post(self):
        data = request.get_json()
        if not data:
            return {'error': 'No data provided'}, 400
        try:
           myorder = MyOrder(
              item = data['item'],
              description = data['description'],
              weight = data['weight'],
              destination = data['destination'],
              cost = data['cost'],
              status = data['status'],
              recipient_name = data['recipient_name'],
              recipient_contact = data['recipient_contact']
           )
           db.session.add(myorder)
           db.session.commit() 
           return make_response(jsonify(myorder.to_dict(), 201))
        
        except Exception as e:
           print("Error:", e) 
           db.session.rollback()
           return {'error': str(e)}, 400
         

api.add_resource(LoginUser, '/loginuser', endpoint='loginuser')
api.add_resource(LoginAdmin, '/loginadmin', endpoint='loginadmin')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(UserList, '/users', endpoint='users')
api.add_resource(Users, '/users/<int:user_id>', endpoint='user')
api.add_resource(MyOrders, '/myorders/<int:myorder_id>', endpoint='myorder')
api.add_resource(MyOrdersList, '/myorders', endpoint='myorders')

# Define Admin-related endpoints
class Admins(Resource):
    def get(self, admin_id=None):
        if admin_id:
            admin = Admin.query.get(admin_id)
            if not admin:
                return make_response(jsonify({'error': 'Admin not found'}), 404)
            return make_response(jsonify(admin.to_dict()), 200)
        else:
            admins = [admin.to_dict() for admin in Admin.query.all()]
            return make_response(jsonify(admins), 200)

api.add_resource(Admins, '/admins', '/admins/<int:admin_id>')

# Define home route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the SendIT API!'}), 200

@app.route('/parcels', methods=['GET'])
def get_parcels():
    parcels = Parcel.query.all()
    return jsonify([{
        'id': parcel.id,
        'parcel_item': parcel.parcel_item,
        'parcel_description': parcel.parcel_description,
        'parcel_weight': parcel.parcel_weight,
        'parcel_cost': parcel.parcel_cost,
        'parcel_status': parcel.parcel_status,
        'user_id': parcel.user_id,
        'destination_id': parcel.destination_id
    } for parcel in parcels]), 200

# Define parcel-related endpoints
@app.route('/parcels', methods=['POST'])
def create_parcel():
    data = request.get_json()
    required_fields = ['parcel_item', 'parcel_weight', 'destination_id']

    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing {field}'}), 400

    current_user = get_jwt_identity()
    new_parcel = Parcel(
        parcel_item=data.get('parcel_item'),
        parcel_description=data.get('parcel_description'),
        parcel_weight=data.get('parcel_weight'),
    
    )
    db.session.add(new_parcel)
    db.session.commit()
    return jsonify({'message': 'Parcel created successfully'}), 201

@app.route('/parcels/<int:parcel_id>', methods=['GET'])
def get_parcel(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    return jsonify({
        'id': parcel.id,
        'parcel_item': parcel.parcel_item,
        'parcel_description': parcel.parcel_description,
        'parcel_weight': parcel.parcel_weight,
        'parcel_cost': parcel.parcel_cost,
        'parcel_status': parcel.parcel_status,
        'user_id': parcel.user_id,
        'destination_id': parcel.destination_id
    }), 200

@app.route('/parcels/<int:parcel_id>', methods=['PATCH'])
def update_parcel(parcel_id):
    data = request.get_json()
    parcel = Parcel.query.get_or_404(parcel_id)
    if 'parcel_item' in data:
        parcel.parcel_item = data['parcel_item']
    if 'parcel_description' in data:
        parcel.parcel_description = data['parcel_description']
    if 'parcel_weight' in data:
        parcel.parcel_weight = data['parcel_weight']
    if 'parcel_cost' in data:
        parcel.parcel_cost = data['parcel_cost']
    if 'destination_id' in data:
        parcel.destination_id = data['destination_id']
        parcel.parcel_cost = calculate_parcel_cost(parcel.destination_id, parcel.parcel_weight)
    if 'parcel_status' in data:
        parcel.parcel_status = data['parcel_status']
    if 'destination_id' in data:
        parcel.destination_id = data['destination_id']
    db.session.commit()
    return jsonify({'message': 'Parcel updated successfully'}), 200

def calculate_parcel_cost(destination_id, weight):
    base_cost = 10
    cost_per_kg = 2
    destination = Destination.query.get(destination_id)
    destination_multiplier = 1.5 if destination else 1
    return base_cost + (weight * cost_per_kg * destination_multiplier)

""" check patch endpoint if it is working on postman """
@app.route('/parcels/<int:parcel_id>', methods=['PATCH'])
#@jwt_required()
def patch_parcel(parcel_id):
    data = request.get_json()
    parcel = Parcel.query.get_or_404(parcel_id)
    current_user = get_jwt_identity()

    if parcel.user_id != current_user['id']:
        return jsonify({'message': 'Unauthorized'}), 403
    if 'destination_id' in data:
        parcel.destination_id = data['destination_id']
    if 'parcel_status' in data:
        parcel.parcel_status = data['parcel_status']

    db.session.commit()
    return jsonify({'message': 'Parcel updated successfully'}), 200

@app.route('/parcels/<int:parcel_id>', methods=['DELETE'])
def delete_parcel(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    db.session.delete(parcel)
    db.session.commit()
    return jsonify({'message': 'Parcel deleted successfully'}), 204

# Define admin-related authentication endpoints
@app.route('/admin/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    try:
        # Access fields using the names from the client-side
        if Admin.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Admin already exists'}), 400

        hashed_password = generate_password_hash(data['password'])
        new_admin = Admin(
            first_name=data['first_name'],  
            last_name=data['last_name'],    
            email=data['email'],
            password_hash=hashed_password
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'message': 'Admin created successfully'}), 201
    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error
        return jsonify({'message': 'An error occurred while creating the admin'}), 500



@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin = Admin.query.filter_by(email=data['email']).first()

    if admin and check_password_hash(admin.password_hash, data['password']):
        access_token = create_access_token(identity=admin.id)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/admin/parcels/<int:parcel_id>/status', methods=['PUT'])
# @jwt_required()
def admin_change_status(parcel_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    admin = Admin.query.get(current_user_id)
    if not admin:
        return jsonify({'message': 'You are not an admin'}), 403
    
    parcel = Parcel.query.get_or_404(parcel_id)
    if 'parcel_status' in data:
        parcel.parcel_status = data['parcel_status']
    if 'destination_id' in data:
        parcel.destination_id = data['destination_id']  # Ensure destination_id is also updated if needed

    db.session.commit()
    return jsonify({'message': 'Status updated successfully'}), 200


# Define destination-related endpoints
@app.route('/destinations', methods=['GET'])
def get_destinations():
    destinations = Destination.query.all()
    return jsonify([{
        'id': destination.id,
        'destination_name': destination.destination_name,
        'destination_address': destination.destination_address
    } for destination in destinations]), 200

@app.route('/destinations/<int:destination_id>', methods=['GET'])
def get_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    return jsonify({
        'id': destination.id,
        'destination_name': destination.destination_name,
        'destination_address': destination.destination_address
    }), 200

@app.route('/destinations', methods=['POST'])
def create_destination():
    data = request.get_json()
    if not data or 'destination_name' not in data or 'destination_address' not in data:
        return jsonify({'message': 'Invalid data'}), 400
    new_destination = Destination(
        destination_name=data['destination_name'],
        destination_address=data['destination_address']
    )
    db.session.add(new_destination)
    db.session.commit()
    return jsonify({'message': 'Destination created successfully'}), 201

@app.route('/destinations/<int:destination_id>', methods=['PATCH'])
def update_destination(destination_id):
    data = request.get_json()
    destination = Destination.query.get_or_404(destination_id)
    if 'destination_name' in data:
        destination.destination_name = data['destination_name']
    if 'destination_address' in data:
        destination.destination_address = data['destination_address']
    db.session.commit()
    return jsonify({'message': 'Destination updated successfully'}), 200


@app.route('/destinations/<int:destination_id>', methods=['DELETE'])
def delete_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    db.session.delete(destination)
    db.session.commit()
    return jsonify({'message': 'Destination deleted successfully'}), 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
