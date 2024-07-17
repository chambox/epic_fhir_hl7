from .model import Model
from app.utils.cache import cache_get, cache_set
from app.services.fhir import FhirService
import time
from typing import Dict

class FhirLocation(Model):

    def __init__(self, id) -> None:
        super().__init__(id)
        self.name = None
        self.status = None
        self.partOf = None
        self.period = {}
    
    @staticmethod
    def fetch_by_id(id: str, encounter_data: Dict = {}):
        """
        Fetch a FHIR location by its ID and associate encounter location data with it.

        This method retrieves a FHIR location object based on the provided `id`. If the
        location is not found in the cache, it fetches the location from the FHIR service,
        stores it in the cache, and then associates the provided `encounter_data` with
        the location before returning it as a `FhirLocation` object.

        Args:
            id (str): A string referencing the FHIR location.
            encounter_data (dict, optional): A dictionary containing encounter data to
                be associated with the FHIR location. Defaults to an empty dictionary.

        Returns:
            FhirLocation: The FHIR location object with the associated encounter data.

        Raises:
            FhirServiceApiException: If there is an error fetching the location from the FHIR service.
        """
        key = f"location-{id}"
        location = cache_get(key)
        if not location:
            time.sleep(1)
            fs = FhirService()
            location = fs.get_location(id)
            cache_set(key, location)

        location['encounter_data'] = encounter_data
        return FhirLocation.extract_factory(location)

    @staticmethod
    def fetch_by_rawdata(encounter_data: Dict = {}):
        """
        Fetch a FHIR location that was returned without a reference over the Encounter entrypoint.

        Args:
            encounter_data (dict, optional): A dictionary containing encounter data to
                be associated with the FHIR location. Defaults to an empty dictionary.

        Returns:
            FhirLocation: The FHIR location object with the associated encounter data.
        Raises:
            KeyError: The ID of the location could not be deduced

        """
        location = {
            "id": encounter_data['location']['identifier']['value'],
            "encounter_data": encounter_data
        }
        return FhirLocation.extract_factory(location)

    @staticmethod
    def extract_factory(rawdata):
        id = rawdata["id"]

        fp = FhirLocation(id)
        fp.rawdata = rawdata
        return fp.get_location()
    
    def get_location(self):

        field_paths = {
            "id": ["id"],
            "name": ["name"],
            "status": ["status"],
            "partOf": ["partOf", "reference"],
            "period": ["period"]
        }

        defaults = {
            "period": {}
        }

        data = {}
        for key in field_paths:
            data[key] = self.get_object_detail(self.rawdata, field_paths[key], defaults.get(key))
        
        self.__dict__.update(data)
        return self
    
    def is_department(self):
        return "managingOrganization" in self.rawdata and "partOf" in self.rawdata
    
    def is_hospital(self):
        # @TODO Look for "inpatient" in type > coding
        def is_tax_code(identifier):
            taxed = [code for code in self.get_object_detail(identifier, ["type", "coding"], []) if code['code'] == "TAX"]
            return len(taxed) > 0
        
        values = [
            ident.get("value").strip() for ident in self.get_object_detail(self.rawdata, ["identifier"], []) 
            if is_tax_code(ident)
        ]

        return len(values) > 0
    
    def is_room(self):
        _is_room =  self.get_object_detail(self.rawdata, ["encounter_data", "physicalType", "coding", 0, "code"]) == "ro"
        if _is_room:
            loc_ref = self.get_object_detail(self.rawdata, ["encounter_data", "location", "reference"])
            loc_id = loc_ref.split("/")[1]
            return FhirLocation.fetch_by_id(loc_id)

    def is_bed(self):
        _is_bed = self.get_object_detail(self.rawdata, ["encounter_data", "physicalType", "coding", 0, "code"]) == "bd"
        if _is_bed:
            return {
                "id": self.get_object_detail(self.rawdata, ["encounter_data", "identifier", "value"])
            }
    
    def get_parent(self):
        parent_id = self.get_object_detail(self.rawdata, ["partOf", "reference"])
        if parent_id:
            return FhirLocation.fetch_by_id(parent_id)
    
    def get_partOf_reference(self):
        if self.partOf:
            return self.partOf.split("/")[-1]
            
        