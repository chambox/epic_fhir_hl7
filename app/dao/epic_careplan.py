from app.services.fhir import FhirService
import json
from app.utils.cache import cache_get, cache_set
from app.dao import Dao

class EpicCarePlanDao(Dao):

    def __init__(self) -> None:
        super().__init__()
    
    def search_data(self, parameters):
        fs = FhirService()
        return fs.search_careplan(parameters)

        