from app.services.fhir import FhirService
import json, traceback
from app.utils.cache import cache_get, cache_set
from app.repository import Repository
from app.models import model_to_dict
from app.models.patient import PatientReference
from app.models.careplan import (
    CarePlan,
    CarePlanParameter,
    CarePlanActivity,
    CarePlanReference,
)


class EpicCarePlanRepository(Repository):
    def __init__(self) -> None:
        super().__init__()
        self.hospital = None
        self.patient = None
        self.care_plans = []
        self.activites = []
        self.externally_provided_weights = []
        self.medications = []

    @staticmethod
    def search_data(parameters):
        try:
            cache_key = f"careplan-{parameters['category']}-{parameters['patient']}"
            api_data = cache_get(cache_key)
            if not api_data:
                fs = FhirService()
                api_data = fs.search_careplan(parameters)
                cache_set(cache_key, api_data, 10000)

            repo = EpicCarePlanRepository()
            repo.set_rawdata(api_data)
            return repo.extract_care_message()

        except Exception as e:
            traceback.print_exc()
            return []

    def extract_care_message(self):
        for entry in self.rawdata["entry"]:
            if self.patient is None:
                self._extract_patient(entry)
            self._extract_care_plan(entry)
            self._extract_entry_activites(entry)

        return {
            "hospital": self.hospital,
            "patient": model_to_dict(self.patient),
            "care_plans": model_to_dict(self.care_plans, is_lsit=True),
            "externally_provided_weights": model_to_dict(
                self.externally_provided_weights, is_lsit=True
            ),
            "activites": model_to_dict(self.activites, is_lsit=True),
            "medications": model_to_dict(self.medications, is_lsit=True),
        }

    def _extract_hospital(self):
        # @TODO: See how to get hospital
        self.hospital = None

    def _extract_patient(self, entry):
        patient_reference = self.get_object_detail(
            entry, ["resource", "subject", "reference"]
        )
        if patient_reference:
            self.patient = PatientReference(id=patient_reference.split("/")[1])

    def _extract_care_plan(self, entry):
        field_paths = {
            "id": ["resource", "id"],
            "version": ["resource", "version"],
            "starts_at": ["resource", "period", "start"],
            "ends_at": ["resource", "period", "end"],
            "name": ["resource", "title"],
            "parameters": [
                "resource",
                "category",
            ],  # label, value, version, type ("string" "number" "boolean")
            "status": ["resource", "status"],
        }

        data = {"parent": None, "department": None}

        for field in field_paths:
            data[field] = self.get_object_detail(entry, field_paths[field])

        data["is_deleted"] = data["status"] in ["cancelled", "deleted"]
        parameters = [
            CarePlanParameter(
                data={
                    "label": "Status",
                    "value": data["status"],
                    "type": "string",
                    "version": None,
                }
            )
        ]
        category = self.get_object_detail(entry, ["resource", "category"])
        if category:
            for c in category:
                parameters.append(
                    CarePlanParameter(
                        data={
                            "label": c["coding"][0]["display"],
                            "value": c["coding"][0]["code"],
                            "type": "number",
                            "version": None,
                        }
                    )
                )

        data["parameters"] = parameters

        care_plan = CarePlan(data=data)
        self.care_plans.append(care_plan)

    def _extract_entry_activites(self, entry):
        activities = self.get_object_detail(entry, ["resource", "activity"], [])
        fs = FhirService()
        for activity in activities:
            try:
                if "extension" in activity:
                    value_ref = activity["extension"][0]["valueReference"]
                    reference = value_ref["reference"].split("/")[1]
                    careplan = self._get_care_plan(fs, reference)
                    ca = self._extract_careplan_activity(careplan)
                    if ca:
                        self.activites.append(ca)
            except:
                traceback.print_exc()

    def _extract_careplan_activity(self, entry):
        field_paths = {
            "id": ["id"],
            "version": ["version"],
            "starts_at": ["period", "start"],
            "ends_at": ["period", "end"],
            "iterations": ["none"],
            "weight": ["none"],
            "executed_percentage": ["none"],
            "care_plan": ["partOf"],
            "department": ["none"],
            "is_deleted": ["none"],
        }

        defaults = {"is_deleted": False}

        data = {}
        for field in field_paths:
            data[field] = self.get_object_detail(
                entry, field_paths[field], defaults.get(field)
            )
        if data["care_plan"]:
            ref = data["care_plan"][0]["reference"].split("/")[1]
            data["care_plan"] = CarePlanReference(id=ref)

        if data["id"]:
            return CarePlanActivity(data=data)

    def _get_care_plan(self, fs: FhirService, reference: str):
        cache_key = f"careplan-{reference}"
        data = cache_get(cache_key)
        if not data:
            data = fs.get_careplan(reference)
            cache_set(cache_key, data, 10000)

        return data
