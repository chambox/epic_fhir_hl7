from app.models import Model


class Bed(Model):
    id: str
    data: dict

    def __init__(self, id: str, data: dict):
        self.id = id
        self.data = data

    def to_dict(self):
        return {
            "id": self.id,
            **self.data
        }
