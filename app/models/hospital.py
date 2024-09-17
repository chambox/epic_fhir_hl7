from app.models import Model


class HospitalReference(Model):
    pass


class HospitalStay(Model):
    def __init__(self, id=None, data={}) -> None:
        self.version = None
        super().__init__(id, data)


class HospitalStayReference(Model):
    pass
