from flask import request, Blueprint, jsonify 
import json
import sqlalchemy.exc
import routes.authentication as authentication
import config.db as db

conn = db.con()
blueprint_route_product = Blueprint(name="product", import_name=__name__)
#================================================PRODUTO=======================================================
#CONSULTA PRODUTO POR ID
@blueprint_route_product.route('/consultaproduto/<cod>',  methods=['GET'])
@authentication.token_required
def consultaproduto(cod):
    query = f'SELECT * FROM produto WHERE cod_prod = {cod};'

    try:
        produto = conn.execute(query).fetchall()

        if produto.__len__() == 0:
            return jsonify('Não há produto cadastrado com esse id')

        l = db.listresult(produto)
        jsonified_data = json.dumps(l)
        return jsonify({"produtos": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')   

#CONSULTA TODOS OS PRODUTOS
@blueprint_route_product.route('/consultaprodutos', methods=['GET'])
@authentication.token_required
def consultaprodutos():
    query = 'SELECT * FROM produto;'

    try:
        produtos = conn.execute(query).fetchall()

        if(produtos.__len__() == 0):
            return jsonify('Não há produtos cadastrados')

        output_data = db.listresult(produtos)

        jsonified_data = json.dumps(output_data)
        return jsonify({"produtos": json.loads(jsonified_data)})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')

#CADASTRO DE PRODUTO
@blueprint_route_product.route('/cadastroproduto', methods=['POST']) 
@authentication.token_required 
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
@blueprint_route_product.route('/atualizaproduto/<cod>', methods=['PUT'])
@authentication.token_required
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
@blueprint_route_product.route('/deletaproduto/<cod>', methods=['DELETE'])
@authentication.token_required 
def deletaproduto(cod):
    query = f'DELETE FROM produto WHERE cod_prod = {cod};'

    try:
        conn.execute(query)
        return jsonify({'message': f'Produto {cod} excluido!'})
    except sqlalchemy.exc.NoResultFound:   
        return jsonify('Falha ao executar consulta no banco')
