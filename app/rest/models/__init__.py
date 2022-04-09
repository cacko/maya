

class AggregatedMeta(type):

    def get_records(cls, *args, **kwargs):
        return cls().query(*args, **kwargs)


class Aggregated(object, metaclass=AggregatedMeta):

    def query(self, *args, **kwargs):
        raise NotImplementedError
