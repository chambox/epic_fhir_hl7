class Model(object):
    def __init__(self, id=None) -> None:
        self.id = id
        self.rawdata = {}

    def get_object_detail(self, _object, field_path, default=None):
        try:
            value = _object
            for key in field_path:
                value = value[key]
            return value
        except (KeyError, IndexError, TypeError):
            return default

    def set_rawdata(self, rawdata):
        self.rawdata = rawdata

    def get_reference_object(self):
        return {"id": self.id}
