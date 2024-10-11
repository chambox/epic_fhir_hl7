class Repository(object):
    def __init__(self) -> None:
        self.rawdata = {}
        self.model = object()

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

    def set_model(self, model):
        if "id" in self.rawdata:
            model.id = self.rawdata["id"]
            self.model = model
