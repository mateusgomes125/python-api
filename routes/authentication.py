from flask import Blueprint, request, session, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import jwt
import config.db as db
import os
from dotenv import load_dotenv

blueprint_route_auth = Blueprint(name="auth", import_name=__name__)

conn = db.con()
load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET')

#================================================VALIDAÇÃO DE USUARIO=======================================================
#LOGIN
@blueprint_route_auth.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    check = False
    query = f'SELECT * FROM usuario WHERE username = \'{username}\';'
    user = conn.execute(query).fetchall()
    for u in user:
        if check_password_hash(u['password'], password):
            check = True 
    
    if user.__len__() != 0 and check:
        session['logged_in'] = True
        token = jwt.encode({
            'user': username,
            'password': password,
            'exp': int((datetime.now() + timedelta(minutes=30)).timestamp())
        },
            SECRET_KEY, algorithm='HS256')
        return jsonify({'token' : token})
    else:
        return make_response('usuario não cadastrado', 403, {'WWW-WAuthenticate' : 'Basic realm: "Authentication Failed!"'})

#VALIDAÇÃO DO TOKEN
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        check = False
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401    
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms='HS256') 
            res = conn.execute(f"SELECT * FROM usuario WHERE username = \'{payload['user']}\'").fetchall()
            if res.__len__() == 0:
                return jsonify({'Error': 'usuario correspondente ao token não está registrado'})
            for u in res:
                if check_password_hash(u['password'], payload['password']):
                    check = check_password_hash(u['password'], payload['password'])
                else:
                    return jsonify({'Error':'falha na validação do token, token depreciado'})                
            if res.__len__() != 0 and check:
                return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Expired token. Reauthentication required.", "authenticated": False,}), 401
        except jwt.InvalidTokenError:
            return jsonify({'Alert' : 'Invalid token!'})
    return decorated
