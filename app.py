from flask import Flask
from views.index import index_blueprint
from views.index import Device
from flask_bootstrap import Bootstrap
from views.index import index
from views.nav import nav, init_custom_nav_renderer

application = Flask(__name__)
application.register_blueprint(index_blueprint)
application.config['SECRET_KEY'] = 'secret'
Bootstrap(application)
nav.init_app(application)
init_custom_nav_renderer(application)