from .model import Model
from .fhir_patient import FhirPatient
from .fhir_location import FhirLocation
from app.services.fhir import FhirService
import json
from app.utils.cache import cache_get, cache_set
from app.models.patient_reference import PatientReference
from app.dao import Dao

class EpicCarePlanDao(Dao):

    def __init__(self, id=None) -> None:
        super().__init__(id)
        self.rooms = {}
        self.beds = {}
        self.hospital_stays = {}
        self.hospitals = {}
        self.department_stays = {}
        self.patient = None