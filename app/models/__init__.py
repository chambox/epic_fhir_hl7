class Model(object):
    def __init__(self, id=None, data={}) -> None:
        self.id = id
        self.set_data(data)

    def set_data(self, data_dict):
        """
        Initializes the DataObject with properties from the dictionary.

        Parameters:
        data_dict (dict): Dictionary containing the data to be assigned as properties.
        """
        for key, value in data_dict.items():
            # if hasattr(self, key): @TODO: define the exact properties of each model and do this check
            setattr(self, key, value)

    def get_reference_object(self):
        return {"id": self.id}

    def to_dict(self):
        _dict = self.__dict__
        for key in _dict:
            _dict[key] = model_to_dict(_dict[key], is_lsit=isinstance(_dict[key], list))

        return _dict


def model_to_dict(obj, is_lsit=False):
    if is_lsit:
        return [model_to_dict(o) for o in obj]

    if isinstance(obj, Model):
        return obj.to_dict()

    return obj
