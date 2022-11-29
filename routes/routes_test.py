from flask import Blueprint
import routes.authentication as authentication

blueprint_route_test = Blueprint(name="test_routes", import_name=__name__)

#================================================ROTAS DE TESTE=======================================================
#public
@blueprint_route_test.route('/public')
def public():
    return 'public access'

#authenticated
@blueprint_route_test.route('/auth')
@authentication.token_required
def auth():
    return 'JWT is verified. Welcome to the dashboard!'