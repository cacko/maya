import typing as t
import os


class ConfigMeta(type):
    _instance: 'Config' = None

    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    def namespace(cls, namespace: str) -> dict:
        return cls().get_namespace(namespace)


class Config(dict, metaclass=ConfigMeta):

    def __init__(self):
        dict.__init__(self, os.environ)

    def get_namespace(
            self,
            namespace: str,
            lowercase:
            bool = True,
            trim_namespace: bool = True
    ) -> t.Dict[str, t.Any]:
        rv = {}
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {dict.__repr__(self)}>"
