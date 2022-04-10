from flask import Flask
from peewee import *
from playhouse.db_url import connect, parse


class StorageMeta(type):
    _app: Flask = None
    config: dict = None
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StorageMeta, cls).__call__(*args, **kwargs)
        return cls._instance

    def register(cls, app: Flask):
        cls._app = app
        cls.config = app.config.get_namespace("DB_")

    @property
    def db(cls) -> PostgresqlDatabase:
        return cls().get_db()


class Storage(object, metaclass=StorageMeta):
    __db: PostgresqlDatabase = None

    def __init__(self):
        parsed = parse(Storage.config.get("url"))
        self.__db: PostgresqlDatabase = PostgresqlDatabase(**parsed)

    def get_db(self) -> PostgresqlDatabase:
        return self.__db
