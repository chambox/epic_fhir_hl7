from .fhir import FhirService
from config import Config
from app.repository.epic_encounter import EpicEncounterRepository
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
            encounter_agreegation = EpicEncounterRepository.extract_factory(encounter)
            if encounter_agreegation:
                self.data.extend(encounter_agreegation)

        return self.data

    def parse_partient_encounters(self, patient_id):
        encounters = self.fetch_patient_encounters(patient_id)
        for encounter in encounters:
            encounter_agreegation = EpicEncounterRepository.extract_factory(encounter)
            if encounter_agreegation:
                self.data.extend(encounter_agreegation)
        return self.data

    def fetch_encounters(self):
        encounters = EpicEncounterRepository.read_test_data()
        if encounters:
            # @TODO check if len is not 0
            return encounters

        fs = FhirService()
        response = fs.get_group(Config.EPIC_FHIR_GROUP_ID)
        listen = True
        tries = 0
        while listen:
            res = fs.listen_bulk_request(response.headers.get("Content-Location"))
            if res is not None and res.strip() not in [""]:
                obj = json.loads(res)
                if "output" in obj:
                    encounter_files = [
                        entry for entry in obj["output"] if entry["type"] == "Encounter"
                    ]
                    encounter_file = encounter_files[0]
                    e_res = fs.bulk_file_request(encounter_file["url"])

                    parts = e_res.text.split("\r\n")

                    encounters = [
                        json.loads(p.strip()) for p in parts if p not in [None, ""]
                    ]

                    # save to file @TODO implement a small database for this
                    cache_set("encounters", encounters)
                    return encounters

            tries = tries + 1
            print(f"No of tries {tries}")
            if tries > CronService.MAX_LISTEN_TRIES:
                listen = False

    def fetch_patient_encounters(self, patient_id):
        """Fetches encounters for a specific patient from either test data or live FHIR data."""
        # First try to fetch test data if available
        encounters = EpicEncounterRepository.read_patient_test_data(patient_id)
        if encounters:
            return encounters

        # If no test data, proceed to fetch from live FHIR service
        try:
            # Directly fetch patient encounters using the patient ID
            encounters = EpicEncounterRepository.read_patient_data(patient_id)
            encounters = [entry["resource"] for entry in encounters["entry"]]
            # Cache the results for performance optimization
            cache_set(f"patient-encounters-{patient_id}", encounters)
            return encounters
        except Exception as e:
            # Log and handle errors appropriately
            print(f"Failed to fetch encounters for patient {patient_id}: {str(e)}")
            return (
                []
            )  # Return an empty list or raise an exception as per your error handling policy
