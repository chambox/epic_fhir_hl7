from app.models import Model


class Patient(Model):
    def __init__(self, id=None, data={}) -> None:
        self.first_name = None
        self.last_name = None
        self.date_of_birth = None
        self.gender = None
        self.is_deleted = None
        self.version = None

        super().__init__(id, data)


class PatientReference(Model):
    pass
