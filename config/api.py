
from flask import Flask 
from dotenv import load_dotenv

import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from routes.routes_test import blueprint_route_test
from routes.user_routes import blueprint_route_user
from routes.authentication import blueprint_route_auth
from routes.client_routes import blueprint_route_client
from routes.products_routes import blueprint_route_product

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET')

app.register_blueprint(blueprint_route_test, url_prefix="/test_routes")
app.register_blueprint(blueprint_route_user, url_prefix="/user")
app.register_blueprint(blueprint_route_auth, url_prefix="/auth")
app.register_blueprint(blueprint_route_client, url_prefix="/client")
app.register_blueprint(blueprint_route_product, url_prefix="/product")

# if __name__ == '__main__':

#     app.run(debug=True)


