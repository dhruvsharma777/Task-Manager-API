from flask import request, jsonify, Blueprint, current_app
from app import db
from app.models import User
import jwt
import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """
    User Registration
    Creates a new user account.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: The desired username for the new account.
              example: mynewuser
            password:
              type: string
              format: password
              description: The desired password for the new account.
              example: Str0ngPa$$w0rd
    responses:
      201:
        description: User registered successfully.
      400:
        description: Bad request (e.g., missing username or password).
      409:
        description: Conflict (a user with that username already exists).
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 409

    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    Authenticates a user and returns a JWT token for accessing protected endpoints.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: The user's username.
              example: mynewuser
            password:
              type: string
              description: The user's password.
              format: password
              example: Str0ngPa$$w0rd
    responses:
      200:
        description: Login successful, token returned.
        schema:
          type: object
          properties:
            token:
              type: string
              description: The JWT token for authenticating future requests.
      401:
        description: Unauthorized (invalid credentials).
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Could not verify'}), 401

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Could not verify'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})