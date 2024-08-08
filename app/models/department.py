from app.models import Model

class DeparmentStay(Model):
    def __init__(self, id=None, data={}) -> None:
        self.version = None
        super().__init__(id, data)

class DeparmentStayLocation(Model):
    pass

class DeparmentReference(Model):
    pass
