
from app.models import Model

class Location(Model):

    def __init__(self, id=None, data={}) -> None:
        super().__init__(id, data)
    
    def get_parent(self):
        from app.dao.epic_location import EpicLocationDao
        if self.partOf:
            return EpicLocationDao.fetch_by_id(self.partOf)

    def get_partOf_reference(self):
        if self.partOf:
            return self.partOf.split("/")[-1]
    
    def has_parent(self):
        return self.get_partOf_reference is not None
        

 