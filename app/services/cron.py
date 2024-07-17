from .fhir import FhirService
from config import Config
from app.models.fhir_encounter import FhirEncounter
from app.utils.cache import cache_set
import json

class CronService(object):

    MAX_LISTEN_TRIES = 5
    data = []

    def __init__(self) -> None:
        pass

    def start(self):
        return self.parse_encounters()

    def parse_encounters(self):
        encounters = self.fetch_encounters()
        for encounter in encounters:
            encounter_agreegation = FhirEncounter.extract_factory(encounter)
            if encounter_agreegation:
                self.data.extend(encounter_agreegation)

        return self.data

    def fetch_encounters(self):
        encounters = FhirEncounter.read_test_data()
        if encounters:
            #@TODO check if len is not 0
            return encounters

        fs = FhirService()
        response = fs.get_group(Config.EPIC_FHIR_GROUP_ID)
        listen = True
        tries = 0
        while (listen):
            res = fs.listen_bulk_request(response.headers.get('Content-Location'))
            if res is not None and res.strip() not in [""]:
                obj = json.loads(res)
                if "output" in obj:
                    encounter_files = [entry for entry in obj['output'] if entry['type'] == 'Encounter']
                    encounter_file = encounter_files[0]
                    e_res = fs.bulk_file_request(encounter_file['url'])

                    parts = e_res.text.split("\r\n")

                    encounters = [json.loads(p.strip()) for p in parts if p not in [None, '']]
                    
                    # save to file @TODO implement a small database for this
                    cache_set('encounters', encounters)
                    return encounters

            tries = tries + 1
            print (f"No of tries {tries}")
            if tries > CronService.MAX_LISTEN_TRIES:
                listen = False

