from app.dao import Dao
from app.utils.cache import cache_get, cache_set
from app.services.fhir import FhirService
from app.models.patient import Patient

class EpicPatientDao(Dao):

    def __init__(self) -> None:
        super().__init__()
    
    @staticmethod
    def fetch_by_id(id):
        key = f"patient-{id}"
        raw_data = cache_get(key)
        if not raw_data:
            fs = FhirService()
            raw_data = fs.get_patient(id)
            cache_set(key, raw_data)

        patient = EpicPatientDao.extract_factory(raw_data)
        if patient.id:
            return patient


    @staticmethod
    def extract_factory(rawdata):
        dao = EpicPatientDao()
        dao.set_rawdata(rawdata)

        return dao.get_patient()
    
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
        data["is_deleted"] = not data["is_deleted"] # should be opposite of active
        
        data['alternative_ids'] = [
            ident.get("value").strip() for ident in self.get_object_detail(self.rawdata, ["identifier"], []) 
            if ident.get("system") != "http://open.epic.com/FHIR/StructureDefinition/patient-dstu2-fhir-id"
        ]

        return Patient(data=data)
