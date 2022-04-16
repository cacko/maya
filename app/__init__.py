from datetime import datetime
from flask import Flask
from flask_session import Session
import logging
import os
from flask.json import JSONEncoder
from flask_cors import CORS
from app.storage import Storage
from app.face.train import Train
from app.s3 import S3


class ISOEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


class ISOFlask(Flask):
    json_encoder = ISOEncoder


def create_app(test_config=None):
    app = ISOFlask(__name__, instance_relative_config=True)
    CORS(app, origins=["http://localhost:4200", "https://maya.cacko.net"],
         allow_header=["etag"],
         expose_headers=["etag", "last-modified"])
    app.config.from_envvar("FLASK_CONFIG")
    app.secret_key = 'kuramijanko'
    sess = Session()
    sess.init_app(app)

    if app.debug or os.environ.get("FLASK_RUN_FROM_CLI", None):
        app.logger.setLevel(logging.DEBUG)
    else:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    Storage.register(app)
    S3.register(app)
    Train.register(app)

    from . import cli
    from . import rest

    app.register_blueprint(cli.bp)
    app.register_blueprint(rest.bp)

    return app
