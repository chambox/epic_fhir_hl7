from app.models import Model


class Encounter(Model):
    def __init__(self, id=None, data={}) -> None:
        super().__init__(id, data)
