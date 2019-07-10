from flask import Flask
from views.index import index_blueprint
from views.index import Device
from flask_bootstrap import Bootstrap
from views.index import index
from views.nav import nav, init_custom_nav_renderer

application = Flask(__name__)
application.register_blueprint(index_blueprint)
Bootstrap(application)
nav.init_app(application)
init_custom_nav_renderer(application)


if __name__ == "__main__":
    application.run(host='0.0.0.0',port=5000)