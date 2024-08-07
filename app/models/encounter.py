from app.models import Model
from app.utils.cache import cache_get, cache_set
from app.services.fhir import FhirService

class Encounter(Model):

    def __init__(self, id=None, data={}) -> None:
        super().__init__(id, data)