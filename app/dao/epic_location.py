from app.dao import Dao
from app.utils.cache import cache_get, cache_set
from app.services.fhir import FhirService
from app.models.location import Location
from app.models.bed_reference import BedReference
import time

class EpicLocationDao(Dao):

    def __init__(self) -> None:
        super().__init__()
    
    @staticmethod
    def fetch_by_id(id: str, encounter_data: dict = {}):
        """
        Fetch a FHIR location by its ID and associate encounter location data with it.

        This method retrieves a FHIR location object based on the provided `id`. If the
        location is not found in the cache, it fetches the location from the FHIR service,
        stores it in the cache, and then associates the provided `encounter_data` with
        the location before returning it as a `Location` object.

        Args:
            id (str): A string referencing the FHIR location.
            encounter_data (dict, optional): A dictionary containing encounter data to
                be associated with the FHIR location. Defaults to an empty dictionary.

        Returns:
            Location: The FHIR location object with the associated encounter data.

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
        return EpicLocationDao.extract_factory(location)

    @staticmethod
    def fetch_by_rawdata(encounter_data: dict = {}):
        """
        Fetch a FHIR location that was returned without a reference over the Encounter entrypoint.

        Args:
            encounter_data (dict, optional): A dictionary containing encounter data to
                be associated with the FHIR location. Defaults to an empty dictionary.

        Returns:
            Location: The FHIR location object with the associated encounter data.
        Raises:
            KeyError: The ID of the location could not be deduced

        """
        location = {
            "id": encounter_data['location']['identifier']['value'],
            "encounter_data": encounter_data
        }
        return EpicLocationDao.extract_factory(location)

    @staticmethod
    def extract_factory(rawdata):
        dao = EpicLocationDao()
        dao.set_rawdata(rawdata)
    
        return dao.get_location()
    
    def get_location(self):

        field_paths = {
            "id": ["id"],
            "name": ["name"],
            "status": ["status"],
            "partOf": ["partOf", "reference"],
            "period": ["period"],
        }

        defaults = {
            "period": {}
        }

        data = {}
        for key in field_paths:
            data[key] = self.get_object_detail(self.rawdata, field_paths[key], defaults.get(key))

        data.update({
            "is_department": self._is_department(),
            "is_hospital": self._is_hospital(),
            "is_room": self._is_room(),
            "is_bed": self._is_bed()
        })

        return Location(data=data)
    
    def _is_department(self):
        return "managingOrganization" in self.rawdata and "partOf" in self.rawdata
    
    def _is_hospital(self):
        # @TODO Look for "inpatient" in type > coding
        def is_tax_code(identifier):
            taxed = [code for code in self.get_object_detail(identifier, ["type", "coding"], []) if code['code'] == "TAX"]
            return len(taxed) > 0
        
        values = [
            ident.get("value").strip() for ident in self.get_object_detail(self.rawdata, ["identifier"], []) 
            if is_tax_code(ident)
        ]

        return len(values) > 0
    
    def _is_room(self):
        # HL7 standard of a room
        _is_room =  self.get_object_detail(self.rawdata, ["encounter_data", "physicalType", "coding", 0, "code"]) == "ro"
        if _is_room:
            loc_ref = self.get_object_detail(self.rawdata, ["encounter_data", "location", "reference"])
            loc_id = loc_ref.split("/")[1]
            return EpicLocationDao.fetch_by_id(loc_id)

    def _is_bed(self):
        # HL7 standard of a bed
        _is_bed = self.get_object_detail(self.rawdata, ["encounter_data", "physicalType", "coding", 0, "code"]) == "bd"
        if _is_bed:
            return BedReference(id=self.get_object_detail(self.rawdata, ["encounter_data", "identifier", "value"]))