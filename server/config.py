from flask_restful import Api
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .utils import safe_str_cmp
import os

app = Flask(__name__, static_folder="moringa/phase5/sendit/sendIT-group-3-client/client/build", static_url_path="/")
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sendit.db' 
app.config['SECRET_KEY'] = 'group 3' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

api = Api(app)

frontend_folder = os.path.join(os.getcwd(), "..", "moringa", "phase5", "sendit", "sendIT-group-3-client","client", "build")
dist_folder = os.path.join(frontend_folder, "dist")

@app.route("/", defaults={'filename': ''})
@app.route("/<path:filename>")
def index(filename):
   if not filename:
     filename = "index.html"   
   return send_from_directory(dist_folder, filename)
     

#api routes

with app.app_context():
    db.create_all()