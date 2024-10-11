from .model import Model
from .fhir_patient import FhirPatient
from .fhir_location import FhirLocation
from app.utils.cache import cache_get
from app.models.patient_reference import PatientReference


class FhirEncounter(Model):
    def __init__(self, id=None) -> None:
        super().__init__(id)
        self.rooms = {}
        self.beds = {}
        self.hospital_stays = {}
        self.hospitals = {}
        self.department_stays = {}
        self.patient = None

    @staticmethod
    def extract_factory(rawdata):
        fe = FhirEncounter(rawdata["id"])
        fe.set_rawdata(rawdata)

        if fe._is_hospital_stay():
            """
            If this Encounter is seen as a hospital stay, then extract the patient and department info
            and return the extracted ADTMessage
            """
            # Extract Patient
            fe._extract_patient()

            # Extract Hospital, HospitalStay and DepartmentStay
            fe._extract_hospital_and_departments()

            # return ADTMessage
            return fe._get_adt_message()

    def _extract_patient(self):
        patient = None
        patient_reference = self.get_object_detail(
            self.rawdata, ["subject", "reference"]
        )
        if patient_reference:
            ref = patient_reference.split("/")[1]
            patient = FhirPatient.fetch_by_id(ref)

            if not patient:
                patient = PatientReference(patient_reference)

        self.patient = patient

    def _extract_hospital_and_departments(self):
        # hospital stay data deduced from the Encounter object (self.rawdata)
        stay_data = {
            "id": self.id,
            "version": None,
            "patient": self.patient
            if self.patient is not None
            else self._extract_patient(),
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

        encounter_locations = self.get_object_detail(self.rawdata, ["location"], [])

        for location in encounter_locations:
            location_reference = self.get_object_detail(
                location, ["location", "reference"], ""
            )

            if location_reference:
                id = location_reference.split("/")[1]
                loc = FhirLocation.fetch_by_id(id, location)
            else:
                loc = FhirLocation.fetch_by_rawdata(location)

            if loc.is_hospital() and not loc.id in self.hospitals:
                self.hospitals[loc.id] = {
                    "fhir_location": loc,
                    "hospital": loc.get_reference_object(),
                    "stay_data": stay_data,
                    "department_stays": [],
                }

            if (
                loc.is_department()
                and not loc.id in self.department_stays
                and "period" in location
            ):
                self.department_stays[loc.id] = {
                    "fhir_location": loc,
                    "hospital_stay": self.id,
                }

                # Check the partOf property of hos location if it is a hospital
                partof_reference = loc.get_partOf_reference()
                if partof_reference:
                    hospital_loc = FhirLocation.fetch_by_id(partof_reference)
                    if (
                        hospital_loc.is_hospital()
                        and not hospital_loc.id in self.hospitals
                    ):
                        self.hospitals[hospital_loc.id] = {
                            "fhir_location": hospital_loc,
                            "hospital": hospital_loc.get_reference_object(),
                            "stay_data": stay_data,
                            "department_stays": [],
                        }
                        # @TODO
                        # Add check to iterate over all saved hospitals to see if hospital reference from partOf is same as hospital
                        # from encounter
                        self.department_stays[loc.id]["hospital_id"] = hospital_loc.id

            if loc.is_room():
                self.rooms[loc.id] = {"fhir_location": loc}

            if loc.is_bed():
                self.beds[loc.id] = {"fhir_location": loc}

        # match hospital and department stays and also rooms and beds in the department
        # This match is done solely based on the partOf property of each FhirLocation
        self._match_beds_to_rooms()
        self._match_rooms_to_departments()
        self._match_departments_to_hospitals()

    def _is_hospital_stay(self):
        return "hospitalization" in self.rawdata

    def _match_beds_to_rooms(self):
        for bed_id in self.beds:
            # get the room id were this bed is located by checking
            # the partOf property of the fhir location object representing this bed
            room_id = self.beds[bed_id]["fhir_location"].get_partOf_reference()
            if room_id:
                if room_id in self.rooms:
                    self.rooms[room_id]["bed"] = self.beds[bed_id][
                        "fhir_location"
                    ].get_reference_object()

    def _match_rooms_to_departments(self):
        for room_id in self.rooms:
            # get the department id were this room is located by checking
            # the partOf property of the fhir location object representing this room
            department_id = self.rooms[room_id]["fhir_location"].get_partOf_reference()
            if department_id:
                if department_id in self.department_stays:
                    self.department_stays[department_id]["room"] = self.rooms[room_id][
                        "fhir_location"
                    ].get_reference_object()

    def _match_departments_to_hospitals(self):
        for department_id in self.department_stays:
            hospital_id = self.department_stays[department_id]["hospital_id"]
            if hospital_id in self.hospitals:
                hospital_reference = self.hospitals[hospital_id][
                    "fhir_location"
                ].get_reference_object()
                if not hospital_id in self.hospital_stays:
                    # create hospital_stay object for this hospital if it does not already exist
                    self.hospital_stays[hospital_id] = self.hospitals[hospital_id][
                        "stay_data"
                    ]
                    self.hospital_stays[hospital_id]["hospital"] = hospital_reference
                    self.hospital_stays[hospital_id]["department_stays"] = []

                # append department stays for a created/existing hospital stay
                self.hospital_stays[hospital_id]["department_stays"].append(
                    {
                        "id": f"{self.id}-{self.department_stays[department_id]['fhir_location'].id}",
                        "hospital_stay": self.get_reference_object(),
                        "version": None,
                        "location": {
                            "hospital": hospital_reference,
                            "venue": hospital_reference,
                            "department": self.department_stays[department_id][
                                "fhir_location"
                            ].get_reference_object(),
                            "room": self.department_stays[department_id].get(
                                "room", None
                            ),
                            "bed": self.department_stays[department_id]
                            .get("room", {})
                            .get("bed"),
                        },
                        "starts_at": self.department_stays[department_id][
                            "fhir_location"
                        ].period.get("start", None),
                    }
                )

    def _get_adt_message(self):
        ret = []
        for hospital_id in self.hospital_stays:
            ds = self.hospital_stays[hospital_id]["department_stays"]
            del self.hospital_stays[hospital_id]["department_stays"]
            ret.append(
                {
                    "hospital": self.hospital_stays[hospital_id]["hospital"],
                    "patient": self.hospital_stays[hospital_id]["patient"],
                    "hospital_stay": self.hospital_stays[hospital_id],
                    "department_stays": ds,
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
        try:
            return cache_get(f"patient-encounters-{patient_id}")
        except:
            return None
