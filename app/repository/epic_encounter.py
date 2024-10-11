import logging

from app.services.fhir import FhirService
from app.utils.cache import cache_get
from app.models.patient import PatientReference
from app.repository import Repository
from app.repository.epic_patient import EpicPatientRepository
from app.repository.epic_location import EpicLocationRepository
from app.models.encounter import Encounter
from app.models.hospital import HospitalStay, HospitalStayReference
from app.models.bed import Bed
from app.models.room import Room
from app.models.hospital import HospitalReference
from app.models.department import (
    DeparmentStay,
    DeparmentStayLocation,
    DeparmentReference,
)
from app.models import model_to_dict
from config import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EpicEncounterRepository(Repository):
    def __init__(self) -> None:
        super().__init__()
        self.rooms = {}
        self.beds = {}

        self.hospitals = {}
        self.hospital_stays = {}

        self.departments = {}
        self.department_stays = {}

        self.department_rooms = {}
        self.room_beds = {}

        self.patient = None
        self.model = Encounter()

    @staticmethod
    def extract_factory(rawdata):
        repo = EpicEncounterRepository()
        repo.set_rawdata(rawdata)

        if repo._is_hospital_stay():
            """
            If this Encounter is seen as a hospital stay, then extract the patient and department info
            and return the extracted ADTMessage
            """
            # Extract Patient
            repo._extract_patient()
            # Extract Hospital, HospitalStay and DepartmentStay
            repo._extract_hospital_and_departments()

            # return ADTMessage
            return repo._get_adt_message()

    def _extract_patient(self):
        patient = None
        patient_reference = self.get_object_detail(
            self.rawdata, ["subject", "reference"]
        )
        if patient_reference:
            ref = patient_reference.split("/")[1]

            # Get the Patient() given reference as ID
            patient = EpicPatientRepository.fetch_by_id(ref)
            if not patient:
                patient = PatientReference(id=patient_reference)

        self.patient = patient

        return self.patient

    def _extract_hospital_and_departments(self):
        # hospital stay data deduced from the Encounter object (self.rawdata)
        stay_data = {
            "id": self.rawdata["id"],
            "version": None,
            "patient": PatientReference(id=self.patient.id),
            "from_at": self.get_object_detail(self.rawdata, ["period", "start"]),
            "until_at": self.get_object_detail(self.rawdata, ["period", "end"]),
            "is_pre_discharge": self.get_object_detail(
                self.rawdata, ["class", "display"]
            )
            == "Discharge",
            "is_pre_admission": self.get_object_detail(
                self.rawdata, ["class", "display"]
            )
            == "Admission",
            "reason_of_discharge": self.get_object_detail(
                self.rawdata, ["hospitalization", "dischargeDisposition", "text"]
            ),
        }

        hospital_stay = HospitalStay(id=self.rawdata["id"], data=stay_data)

        encounter_locations = self.get_object_detail(self.rawdata, ["location"], [])

        for location in encounter_locations:
            location_reference = self.get_object_detail(
                location, ["location", "reference"], ""
            )

            if location_reference:
                id = location_reference.split("/")[1]
                loc = EpicLocationRepository.fetch_by_id(id, location)
            else:
                loc = EpicLocationRepository.fetch_by_rawdata(location)

            if loc.is_hospital and not loc.id in self.hospitals:
                self.hospitals[loc.id] = loc

            if (
                loc.is_department
                and not loc.id in self.departments
                and "period" in location
            ):
                self.departments[loc.id] = loc

                # Check the partOf property of this location if it is a hospital
                partof_reference = loc.get_partOf_reference()
                if partof_reference:
                    hospital_loc = EpicLocationRepository.fetch_by_id(partof_reference)
                    if (
                        hospital_loc.is_hospital
                        and not hospital_loc.id in self.hospitals
                    ):
                        self.hospitals[hospital_loc.id] = loc

                        # @TODO
                        # Add check to iterate over all saved hospitals to see
                        # if hospital reference from partOf is same as hospital from encounter

                        # Arbitriary append of hospital_id to this department to later match hospital to department
                        self.departments[loc.id].hospital_id = hospital_loc.id

            if loc.is_room:
                self.rooms[loc.id] = loc

            if loc.is_bed:
                self.beds[loc.id] = loc

        # match hospital and department stays and also rooms and beds in the department
        # This match is done solely based on the partOf property of each Location from EPIC
        self._match_beds_to_rooms()
        self._match_rooms_to_departments()
        self._match_departments_to_hospitals(hospital_stay)

    def _is_hospital_stay(self):
        return "hospitalization" in self.rawdata

    def _match_beds_to_rooms(self):
        for bed_id in self.beds:
            room_id = self.beds[bed_id].get_partOf_reference()
            if room_id and room_id in self.rooms:
                bed = Bed(id=bed_id, data=self.beds[bed_id].to_dict())
                self.room_beds[room_id] = bed


    def _match_rooms_to_departments(self):
        for room_id in self.rooms:
            department_id = self.rooms[room_id].get_partOf_reference()
            if department_id and department_id in self.departments:
                room = Room(id=room_id, data=self.rooms[room_id].to_dict())
                self.department_rooms[department_id] = room
   

    def _match_departments_to_hospitals(self, hospital_stay: HospitalStay):
        for department_id in self.departments:
            hospital_id = self.departments[department_id].hospital_id

            if hospital_id in self.hospitals:
                if not hospital_id in self.hospital_stays:
                    # create hospital_stay object for this hospital if it does not already exist
                    self.hospital_stays[
                        hospital_id
                    ] = hospital_stay  # a HospitalStay object
                    self.hospital_stays[hospital_id].hospital = HospitalReference(
                        id=hospital_id
                    )
                    self.department_stays[hospital_id] = []

                # append department stays for a created/existing hospital stay
                hs = self.hospital_stays[hospital_id]  # HospitalStay
                ds = self.departments[department_id]  # DepartmentStay
                room = self.department_rooms.get(department_id, None)  # RoomReference

                ds_location = DeparmentStayLocation(
                    data={
                        "hospital": HospitalReference(id=hospital_id),
                        "venue": HospitalReference(id=hospital_id),
                        "department": DeparmentReference(
                            id=department_id
                        ),  # self.departments[department_id]['fhir_location'].get_reference_object(),
                        "room": {'id':self.department_rooms.get(department_id)},
                        "bed": {'id':self.room_beds.get(room.id) if room is not None else None},
                    }
                )
                self.department_stays[hospital_id].append(
                    DeparmentStay(
                        data={
                            "id": f"{hs.id}-{department_id}",
                            "hospital_stay": HospitalStayReference(
                                id=hospital_stay.id
                            ),  # HospitalStayReference object
                            "version": None,
                            "location": ds_location,
                            "starts_at": ds.period.get("start", None),
                        }
                    )
                )

    def _get_adt_message(self):
        ret = []
        for hospital_id in self.hospital_stays:
            ret.append(
                {
                    "hospital": model_to_dict(
                        self.hospital_stays[hospital_id].hospital
                    ),
                    "patient": model_to_dict(self.patient),
                    "hospital_stay": model_to_dict(self.hospital_stays[hospital_id]),
                    "department_stays": model_to_dict(
                        self.department_stays[hospital_id], is_lsit=True
                    ),
                }
            )
        return ret

    @staticmethod
    def read_test_data():
        try:
            return cache_get("encounters")
        except:
            return None

    @staticmethod
    def read_patient_test_data(patient_id):
        # Do not use test data in production
        if Config.TNT_ENVIRONMENT == "production":
            return None

        try:
            return cache_get(f"patient-encounters-{patient_id}")
        except:
            return None
    
    @staticmethod
    def read_patient_data(patient_id):
        fs = FhirService()
        return fs.get_patient_encounters(patient_id)
