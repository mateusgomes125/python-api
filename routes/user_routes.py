from flask import request, Blueprint, jsonify #,session, render_template,  make_response
from werkzeug.security import generate_password_hash, check_password_hash
import json
import sqlalchemy.exc
import routes.authentication as authentication
import config.db as db
# import api

blueprint_route_user = Blueprint(name="user", import_name=__name__)

# app = api.app()
conn = db.con()

#================================================USUARIOS=======================================================
#CADASTRAR NOVO USUARIO NO BANCO
@blueprint_route_user.route('/cadastrausuario', methods=['POST'])
def cadastrausuario(): 
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

#CONSULTA TODOS OS USUARIOS
@blueprint_route_user.route('/consultausuarios', methods= ['GET'])
@authentication.token_required
def consultaregistros():

    select = 'SELECT * FROM usuario;'

    try:
        usuarios = conn.execute(select).fetchall()

        if usuarios.__len__() == 0:
            return jsonify('Não há usuarios cadastrados')
        output_data = db.listresult(usuarios)

        jsonified_data = json.dumps(output_data)

        return jsonify({'usuarios': json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CONSULTA USUARIO PELO ID
@blueprint_route_user.route('/consultausuario/<user>', methods=['GET'])
@authentication.token_required
def consultausuario(user):
    
    select = f'SELECT * FROM usuario WHERE username = \'{user}\';'
    try:
        result = conn.execute(select).fetchall()
        
        if result.__len__() == 0:
            return jsonify('Não há usuario com esse username registrado!')
        
        output_data = db.listresult(result)
        jsonified_data = json.dumps(output_data)
        return jsonify({'usuario': json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#ATUALIZA O USUARIO PELO ID
@blueprint_route_user.route('/atualizausuario/<user>', methods = ['PUT'])
@authentication.token_required
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
@blueprint_route_user.route('/deletausuario/<user>', methods=['DELETE'])
@authentication.token_required
def deletausuario(user):
    delete = f'DELETE FROM usuario WHERE username = \'{user}\';'

    try:
        conn.execute(delete)
        return jsonify(f'usuario \'{user}\' foi removido')
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')   
