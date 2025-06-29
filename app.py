from flask import Flask, jsonify, render_template
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stackover.db'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)


user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}


# Model
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Parsers
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name is required")
user_args.add_argument('email', type=str, required=True, help="Email is required")
user_args.add_argument('password', type=str, required=True, help="Password is required")

login_args = reqparse.RequestParser()
login_args.add_argument('email', type=str, required=True)
login_args.add_argument('password', type=str, required=True)

# Marshaling fields
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}

# Resources
class Register(Resource):
    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        if UserModel.query.filter_by(email=args['email']).first():
            abort(409, message="Email already registered")
        user = UserModel(name=args['name'], email=args['email'])
        user.set_password(args['password'])
        db.session.add(user)
        db.session.commit()
        return user, 201

class Login(Resource):
    def post(self):
        args = login_args.parse_args()
        user = UserModel.query.filter_by(email=args['email']).first()
        if not user or not user.check_password(args['password']):
            abort(401, message="Invalid credentials")
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
class Users(Resource):
        @marshal_with(user_fields)
        @jwt_required()
        def get(self):
            users = UserModel.query.all()
            return users

        @marshal_with(user_fields)
        @jwt_required()
        def post(self):
            args = user_args.parse_args()
            if UserModel.query.filter_by(email=args['email']).first():
                abort(409, message="Email already exists")
            user = UserModel(name=args['name'], email=args['email'])
            user.set_password(args['password'])
            db.session.add(user)
            db.session.commit()
            return user, 201

class User(Resource):
            @marshal_with(user_fields)
            @jwt_required()
            def patch(self, id):
                user = UserModel.query.get(id)
                if not user:
                    abort(404, message="User not found")
                if user.id != int(get_jwt_identity()):
                    abort(403, message="Unauthorized to edit this user")
                args = user_args.parse_args()
                user.name = args['name']
                user.email = args['email']
                user.set_password(args['password'])
                db.session.commit()
                return user

            @marshal_with(user_fields)
            @jwt_required()
            def delete(self, id):
                user = UserModel.query.get(id)
                if not user:
                    abort(404, message="User not found")
                if user.id != int(get_jwt_identity()):
                    abort(403, message="Unauthorized to delete this user")
                db.session.delete(user)
                db.session.commit()
                return user, 204


# Add routes
api.add_resource(Register, '/api/register')
api.add_resource(Login, '/api/login')
api.add_resource(Users, '/api/users')
api.add_resource(User, '/api/users/<int:id>')


# Root route

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the StackOver API",
        "status": "online"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Auto-create tables
    app.run(debug=True)