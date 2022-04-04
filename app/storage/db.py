from flask import Flask
from peewee import *
from playhouse.db_url import connect, parse


class StorageMeta(type):
    _app: Flask = None
    _config: dict = None
    _instance = None
    _db: PostgresqlDatabase = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StorageMeta, cls).__call__(*args, **kwargs)
        return cls._instance

    def register(cls, app: Flask):
        cls._app = app
        cls._config = app.config.get_namespace("DB_")
        parsed = parse(cls._config.get("url"))
        cls._db: PostgresqlDatabase = PostgresqlDatabase(**parsed)
        cls._instance = cls()

    @property
    def db(cls) -> PostgresqlDatabase:
        return cls._db


class Storage(object, metaclass=StorageMeta):
    pass
