from datetime import datetime
from re import A
from flask import Flask, request, current_app
import logging
import os
from flask.json import JSONEncoder
from flask_cors import CORS

from app.cache import Cache
from app.storage import Storage


class ISOEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return super().default(o)


class ISOFlask(Flask):
    json_encoder = ISOEncoder


def create_app(test_config=None):

    app = ISOFlask(__name__, instance_relative_config=True)
    CORS(app, origins=["http://localhost:4200"])
    app.config.from_envvar("FLASK_CONFIG")
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


    Cache.register(app)
    Storage.register(app)


    from . import cli
    from . import api

    app.register_blueprint(cli.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint

    return app
