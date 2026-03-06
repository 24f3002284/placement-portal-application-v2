import os
from flask import Flask
from application.models import db, User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from application.config import LocalConfig
from flask_cors import CORS
from application.celery_init import celery_init_app
from flask_mail import Mail
from flask_caching import Cache

from application.celery_init import  celery_init_app

cache = Cache()


def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalConfig)

    db.init_app(app)
    Mail(app)
    cache.init_app(app)

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore, register_blueprint=False)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Create static folder for CSV exports
    os.makedirs(os.path.join(app.root_path, "static"), exist_ok=True)

    @app.errorhandler(401)
    def unauthorized(e):
        return {"message": "Auth Required"}, 401

    @app.errorhandler(403)
    def forbidden(e):
        return {"message": "You are not allowed to view this route"}, 403

    app.app_context().push()
    return app


app = create_app()
celery = celery_init_app(app)

from application.initial_data import *
from application.routes import *

if __name__ == "__main__":
    app.run(debug=True)