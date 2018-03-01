# -*- coding:utf-8 -*-
import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from flask import Flask
import traceback
from flask import render_template
from flask_script import Manager, Server
from meier_app.commons.logger import logger
from meier_app.extensions import db, login_manager, sentry, compress

__all__ = ['create_app']


def create_app():
    app = Flask(__name__, static_url_path="", static_folder="static")
    configure_app(app)
    configure_extensions(app)
    configure_blueprints(app)
    configure_jinja(app)
    configure_error_handlers(app)
    return app


def configure_blueprints(app):
    from meier_app.resources import resource_blueprints
    blueprints = resource_blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_app(app):
    from meier_app.config import meier_config
    app.config['MEIER_CONFIG'] = meier_config
    app.config['DEBUG'] = True

    if 'SQLALCHEMY_DATABASE_URI' in app.config['MEIER_CONFIG']:
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['MEIER_CONFIG']['SQLALCHEMY_DATABASE_URI']
        app.config["SQLALCHEMY_MAX_OVERFLOW"] = -1
        app.config["SQLALCHEMY_ECHO"] = False
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 20
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


def configure_extensions(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    compress.init_app(app)
    #login_manager.init_app(app)


def configure_error_handlers(app):
    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("/errors/401.html"), 401

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("/errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("/errors/404.html"), 500


def configure_jinja(app):
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True



app = create_app()
app.run(port=8080)

