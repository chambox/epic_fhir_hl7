from .model import Model
from app.utils.cache import cache_get, cache_set
from app.services.fhir import FhirService

class FhirPatient(Model):

    def __init__(self, id) -> None:
        super().__init__(id)
    
    @staticmethod
    def fetch_by_id(id):
        key = f"patient-{id}"
        patient = cache_get(key)
        if not patient:
            fs = FhirService()
            patient = fs.get_patient(id)
            cache_set(key, patient)

        return FhirPatient.extract_factory(patient)


    @staticmethod
    def extract_factory(rawdata):
        id = rawdata["id"]

        fp = FhirPatient(id)
        fp.rawdata = rawdata
        return fp.get_patient()
    
    def get_patient(self):

        field_paths = {
            "id": ["id"],
            "version": ["data", "version"],
            "first_name": ["name", 0, "given", 0],
            "last_name": ["name", 0, "family"],
            "date_of_birth": ["birthDate"],
            "gender": ["gender"],
            "is_deleted": ["active"],
        }

        data = {}
        for key in field_paths:
            data[key] = self.get_object_detail(self.rawdata, field_paths[key])
        
        data['alternative_ids'] = [
            ident.get("value").strip() for ident in self.get_object_detail(self.rawdata, ["identifier"], []) 
            if ident.get("system") != "http://open.epic.com/FHIR/StructureDefinition/patient-dstu2-fhir-id"
        ]

        return data