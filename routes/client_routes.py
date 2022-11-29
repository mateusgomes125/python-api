from flask import request, Blueprint, jsonify #,session, render_template,  make_response
import json
import sqlalchemy.exc
import routes.authentication as authentication
import config.db as db

conn = db.con()
blueprint_route_client = Blueprint(name="client", import_name=__name__)

#================================================CLIENTE=======================================================
#CONSULTA CLIENTE POR ID
@blueprint_route_client.route('/consultacliente/<cod>', methods=['GET'])
@authentication.token_required
def consultacliente(cod):
    query = f'SELECT * FROM clientes WHERE cod_cli = {cod};'
    try:
        cliente = conn.execute(query).fetchall()

        if cliente.__len__() == 0:
            return jsonify('Não há cliente cadastrado com esse id')

        output_data = db.listresult(cliente)
        jsonified_data = json.dumps(output_data)        
        return jsonify({"clientes": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CONSULTA TODOS OS CLIENTES
@blueprint_route_client.route('/consultaclientes',  methods=['GET'])
@authentication.token_required
def consultaclientes():
    query = 'SELECT * FROM clientes;'

    try:
        clientes = conn.execute(query).fetchall()

        if(clientes.__len__() == 0):
            return jsonify('Não há clientes cadastrados')

        output_data = db.listresult(clientes)

        jsonified_data = json.dumps(output_data)
        return jsonify({"produtos": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CADASTRO DE CLIENTE 
@blueprint_route_client.route('/cadastrocliente', methods=['POST']) 
@authentication.token_required
def cadastrocliente():
    cod_cli = request.json['cod_cli']
    endereco = request.json['endereco']
    bairro = request.json['bairro']
    cep = request.json['cep']
    cod_cid = request.json['cod_cid']
    telefone = request.json['telefone'] 
    razao_social = request.json['razao_social']

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
@blueprint_route_client.route('/atualizacliente/<cod>', methods=['PUT'])
@authentication.token_required
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
@blueprint_route_client.route('/deletacliente/<cod>', methods=['DELETE'])
@authentication.token_required 
def deletacliente(cod):
    query = f'DELETE FROM clientes WHERE cod_cli = {cod};'

    try:
        conn.execute(query)
        return jsonify({'message': f'cliente {cod} excluido!'})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')
