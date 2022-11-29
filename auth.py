from flask import Flask, request, session, render_template, jsonify, make_response
# import hashlib
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import sqlalchemy.exc
# from sqlalchemy.ext.declarative import declarative_base  
# from sqlalchemy.orm import sessionmaker
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
# import sqlalchemy_serializer
from werkzeug.security import generate_password_hash, check_password_hash
# import psycopg2
# import main  
#

# a = main.res

app = Flask(__name__)


#================================================CONEXÃO COM O BANCO=======================================================
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET')
username = os.getenv('USERNAME')
path = os.getenv('HOST')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')
db_name = os.getenv('DB')

db_string = f"postgresql://{username}:{password}@{path}:{port}/{db_name}" #USAR .format com parametro {}
db = create_engine(db_string)
conn = db.connect()

AUTHSECRET = 'veplex123'

#================================================ROTAS DE TESTE=======================================================
#public
@app.route('/public')
def public():
    print(os.getenv('HOST'))
    # print(a)
    print(f"postgresql://{username}:{password}@{path}:{port}/{db_name}")
    return 'public access'

#home
@app.route('/')
def home():
     if not session.get('logged_in'):
        return render_template('login.html')
     else:
        return 'Logged in currently'

#================================================REGISTRO E VALIDAÇÃO=======================================================
#REGISTRAR NOVO USUARIO NO BANCO
@app.route('/registrar', methods=['POST'])
def register(): 
    username = request.json['username']
    password = request.json['password']
    hashed_password = generate_password_hash(password, 'pbkdf2:sha256')

    try:
        query = f"SELECT * FROM usuario WHERE username = \'{username}\';"   

        user = conn.execute(query).fetchall()
        print(user.__len__())

        if user.__len__() != 0:
            return jsonify({'message': 'Registro já existe!'})

        query = f'INSERT INTO usuario (username, password) VALUES (\'{username}\', \'{hashed_password}\');'
        conn.execute(query)   
        return jsonify({'message':'novo usuario registrado', 'user' :username, 'password:' : hashed_password})
    except:
        return jsonify({'message': 'Falha ao registrar usuario'})

#LOGIN
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    # hashed_password = generate_password_hash(password)
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
            app.config['SECRET_KEY'], algorithm='HS256')
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
        print(token)     
               
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256') 
            print(payload['user'])
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

# #authenticated
# @app.route('/auth')
# @token_required
# def auth():
#     return 'JWT is verified. Welcome to the dashboard!'

#================================================USUARIOS=======================================================
#CONSULTA TODOS OS USUARIOS
@app.route('/consultausuarios', methods= ['GET'])
@token_required
def consultaregistros():

    select = 'SELECT * FROM usuario;'

    try:
        usuarios = conn.execute(select).fetchall()

        if usuarios.__len__() == 0:
            return jsonify('Não há usuarios cadastrados')
        output_data = listresult(usuarios)

        jsonified_data = json.dumps(output_data)

        return jsonify({'usuarios': json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CONSULTA USUARIO PELO ID
@app.route('/consultausuario/<user>', methods=['GET'])
@token_required
def consultausuario(user):

    select = f'SELECT * FROM usuario WHERE username = \'{user}\';'
    try:
        result = conn.execute(select).fetchall()

        if result.__len__() == 0:
            return jsonify('Não usuario com esse username registrado!')
        
        output_data = listresult(result)
        jsonified_data = json.dumps(output_data)
        return jsonify({'usuario': json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#ATUALIZA O USUARIO PELO ID
@app.route('/atualizausuario/<user>', methods = ['PUT'])
@token_required
def atualizausuario(user):

    username = request.json['username']
    password = request.json['password']

    hashed_password = generate_password_hash(password)

    select = f'SELECT * FROM usuario WHERE username = \'{user}\';'
    
    usuario = conn.execute(select).fetchall()

    if usuario.__len__() == 0:
        return jsonify('Não há cliente cadastrado com esse id')

    update = f'UPDATE usuario SET username = \'{username}\', password = \'{hashed_password}\' WHERE username = \'{user}\';' 

    try:
        conn.execute(update)

        return jsonify(f'usuario {user} foi atualizado')
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')
        
#DELETA O USUARIO PELO ID
@app.route('/deletausuario/<user>', methods=['DELETE'])
@token_required
def deletausuario(user):
    delete = f'DELETE FROM usuario WHERE username = \'{user}\';'

    try:
        conn.execute(delete)
        return jsonify(f'usuario \'{user}\' foi removido')
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')   

#================================================CLIENTE=======================================================
#CONSULTA CLIENTE POR ID
@app.route('/consultacliente/<cod>', methods=['GET'])
@token_required
def consultacliente(cod):
    query = f'SELECT * FROM clientes WHERE cod_cli = {cod};'
    try:
        cliente = conn.execute(query).fetchall()

        if cliente.__len__() == 0:
            return jsonify('Não há cliente cadastrado com esse id')

        output_data = listresult(cliente)
        jsonified_data = json.dumps(output_data)        
        return jsonify({"clientes": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CONSULTA TODOS OS CLIENTES
@app.route('/consultaclientes',  methods=['GET'])
@token_required
def consultaclientes():
    query = 'SELECT * FROM clientes;'

    try:
        clientes = conn.execute(query).fetchall()

        if(clientes.__len__() == 0):
            return jsonify('Não há clientes cadastrados')

        output_data = listresult(clientes)
        print(output_data)
        jsonified_data = json.dumps(output_data)
        return jsonify({"produtos": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CADASTRO DE CLIENTE 
@app.route('/cadastrocliente', methods=['POST']) 
@token_required
def cadastrocliente():
    cod_cli = request.json['cod_cli']
    endereco = request.json['endereco']
    bairro = request.json['bairro']
    cep = request.json['cep']
    cod_cid = request.json['cod_cid']
    telefone = request.json['telefone'] 
    razao_social = request.json['razao_social']

    value = (cod_cli, endereco, bairro, cep, cod_cid, telefone, razao_social)

    sql = f"""INSERT INTO 
                clientes (cod_cli, endereco, bairro, cep, cod_cid, telefone, razao_social) 
            VALUES ({cod_cli}, \'{endereco}\', \'{bairro}\', \'{cep}\', {cod_cid}, \'{telefone}\', \'{razao_social}\')"""
    select = f'SELECT * FROM clientes WHERE cod_cli = {cod_cli}'
    
    try:
        res = conn.execute(select).fetchall()

        if res.__len__() != 0:
           return jsonify({'message' : 'Codigo do cliente já existente'}) 
        else:
            print('codigo valido para inserção')

        conn.execute(sql)

        return jsonify({'message' : f'Cliente {cod_cli} inserido'})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#ATUALIZA CLIENTE PELO ID
@app.route('/atualizacliente/<cod>', methods=['PUT'])
@token_required
def atualizacliente(cod): 

    select = f'SELECT * FROM clientes WHERE cod_cli = {cod}'
    cliente = conn.execute(select).fetchall()

    cod_cli = request.json['cod_cli']
    endereco = request.json['endereco']
    bairro = request.json['bairro']
    cep = request.json['cep']
    cod_cid = request.json['cod_cid']
    telefone = request.json['telefone'] 
    razao_social = request.json['razao_social']    

    if cliente.__len__() == 0:
        return jsonify({'message' : 'cliente não cadastrado', 'data' : {}}), 404   
    try: 
        query = f"""UPDATE clientes SET 
        cod_cli = {cod_cli}, endereco = \'{endereco}\', bairro = \'{bairro}\', cep = \'{cep}\', cod_cid = \'{cod_cid}\', telefone = \'{telefone}\', razao_social = \'{razao_social}\' 
        WHERE cod_cli = {cod}"""
        conn.execute(query)

        return jsonify({'message' : f'cliente {cod_cli} atualizado'}), 201
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#DELETA CLIENTE POR ID
@app.route('/deletacliente/<cod>', methods=['DELETE'])
@token_required 
def deletacliente(cod):
    query = f'DELETE FROM clientes WHERE cod_cli = {cod};'

    try:
        conn.execute(query)
        return jsonify({'message': f'cliente {cod} excluido!'})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#================================================PRODUTO=======================================================
#CONSULTA PRODUTO POR ID
@app.route('/consultaproduto/<cod>',  methods=['GET'])
@token_required
def consultaproduto(cod):
    query = f'SELECT * FROM produto WHERE cod_prod = {cod};'

    try:
        produto = conn.execute(query).fetchall()

        if produto.__len__() == 0:
            return jsonify('Não há produto cadastrado com esse id')

        l = listresult(produto)
        jsonified_data = json.dumps(l)
        return jsonify({"produtos": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')   

#CONSULTA TODOS OS PRODUTOS
@app.route('/consultaprodutos', methods=['GET'])
@token_required
def consultaprodutos():
    query = 'SELECT * FROM produto;'

    try:
        produtos = conn.execute(query).fetchall()

        if(produtos.__len__() == 0):
            return jsonify('Não há produtos cadastrados')

        output_data = listresult(produtos)
        print(output_data)
        jsonified_data = json.dumps(output_data)
        return jsonify({"produtos": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CADASTRO DE PRODUTO
@app.route('/cadastroproduto', methods=['POST']) 
@token_required 
def cadastroproduto():
    cod_prod = request.json['cod_prod']
    nome = request.json['nome']
    descricao = request.json['descricao']
    preco = request.json['preco'] 

    value = (cod_prod, nome, descricao, preco)

    sql = f"""INSERT INTO produto (cod_prod, nome, descricao, preco) VALUES ({cod_prod}, \'{nome}\', \'{descricao}\', {preco});"""
    select = f'SELECT * FROM produto WHERE cod_prod = {cod_prod}'

    try:
        res = conn.execute(select).fetchall()
        
        if res.__len__() != 0:
           return jsonify({'message' : 'Codigo do produto já existente'}) 
        else:
            print('codigo valido para inserção')
        print(sql)
        conn.execute(sql)

        return jsonify({'message' : f'Produto {cod_prod} inserido'})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#ATUALIZA PRODUTO PELO ID
@app.route('/atualizaproduto/<cod>', methods=['PUT'])
@token_required
def atualizaproduto(cod):
    select = f'SELECT * FROM produto WHERE cod_prod = {cod}'
    produto = conn.execute(select).fetchall()

    cod_prod = request.json['cod_prod']
    nome = request.json['nome']
    descricao = request.json['descricao']
    preco = request.json['preco']    

    if produto.__len__() == 0:
        return jsonify({'message' : 'produto não cadastrado'}), 404   
    try: 
        query = f"""UPDATE produto SET 
        cod_prod = {cod_prod}, nome = \'{nome}\', descricao = \'{descricao}\', preco = {preco} WHERE cod_prod = {cod}"""
        conn.execute(query)

        return jsonify({'message' : f'produto {cod_prod} atualizado'}), 201
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#DELETA PRODUTO POR ID
@app.route('/deletaproduto/<cod>', methods=['DELETE'])
@token_required 
def deletaproduto(cod):
    query = f'DELETE FROM produto WHERE cod_prod = {cod};'

    try:
        conn.execute(query)
        return jsonify({'message': f'Produto {cod} excluido!'})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#================================================FUNÇÕES=======================================================
def listresult(result):
    res = {}
    l = []

    for p in result:
        res.update(p)
        # print(res)        
        l.append(tuple(p))
        # print(tuple(p))
    keys = res.keys()
    output_data = [{i:j for i,j in zip(keys,k)} for k in l] 

    return output_data


# user = resquest.form.get('user')
# password = resquest.form.get('password')

# hashed_password = hashlib.sha256(bytes(password, 'utf-8'))
# hashed = hashed_password.hexdigest()

# def authenticate(user, password):
#     encoded_jwt = jwt.encode({'user': user, 'password': password}, AUTHSECRET, algorithm='HS256')


if __name__ == '__main__':

    app.run(debug=True)