from app.utils.cache import cache_get, cache_set
from app.models.patient import PatientReference
from app.dao import Dao
from app.dao.epic_patient import EpicPatientDao
from app.dao.epic_location import EpicLocationDao
from app.models.encounter import Encounter
from app.models.hospital_stay import HospitalStay, HospitalStayReference
from app.models.bed_reference import BedReference
from app.models.room_reference import RoomReference
from app.models.hospital_reference import HospitalReference
from app.models.department_reference import DeparmentReference
from app.models.department_stay import DeparmentStay, DeparmentStayLocation
from app.models import model_to_dict


class EpicEncounterDao(Dao):

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
        dao = EpicEncounterDao()
        dao.set_rawdata(rawdata)

        if dao._is_hospital_stay():
            """
            If this Encounter is seen as a hospital stay, then extract the patient and department info
            and return the extracted ADTMessage
            """
            # Extract Patient
            dao._extract_patient()
            # Extract Hospital, HospitalStay and DepartmentStay
            dao._extract_hospital_and_departments()

            # return ADTMessage
            return dao._get_adt_message()

    def _extract_patient(self):
        patient = None
        patient_reference = self.get_object_detail(self.rawdata, ["subject", "reference"])
        if patient_reference:
            ref = patient_reference.split("/")[1]

            # Get the Patient() given reference as ID
            patient = EpicPatientDao.fetch_by_id(ref)
            if not patient:
                patient = PatientReference(patient_reference)

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
            "is_pre_discharge": self.get_object_detail(self.rawdata, ["class", "display"]) == "Discharge",
            "is_pre_admission": self.get_object_detail(self.rawdata, ["class", "display"]) == "Admission",
            "reason_of_discharge": self.get_object_detail(self.rawdata, ["hospitalization", "dischargeDisposition", "text"])
        }

        hospital_stay = HospitalStay(id=self.rawdata["id"], data=stay_data)

        encounter_locations = self.get_object_detail(self.rawdata, ["location"],[])

        for location in encounter_locations:
            location_reference = self.get_object_detail(location, ["location", "reference"], "")

            if location_reference:
                id = location_reference.split("/")[1]
                loc = EpicLocationDao.fetch_by_id(id, location)
            else:
                loc = EpicLocationDao.fetch_by_rawdata(location)

            if loc.is_hospital and not loc.id in self.hospitals:
                self.hospitals[loc.id] = loc

            if loc.is_department and not loc.id in self.departments and 'period' in location:
                self.departments[loc.id] = loc

                # Check the partOf property of this location if it is a hospital
                partof_reference = loc.get_partOf_reference()
                if partof_reference:
                    hospital_loc = EpicLocationDao.fetch_by_id(partof_reference)
                    if hospital_loc.is_hospital and not hospital_loc.id in self.hospitals:
                        self.hospitals[hospital_loc.id] = loc

                        #@TODO
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
            # get the room id were this bed is located by checking
            # the partOf property of the fhir Location object representing this bed
            room_id = self.beds[bed_id].get_partOf_reference()
            if room_id:
                if room_id in self.rooms:
                    self.room_beds[room_id] = BedReference(id=bed_id) #self.beds[bed_id]["fhir_location"].get_reference_object()

    def _match_rooms_to_departments(self):
        for room_id in self.rooms:
            # get the department id were this room is located by checking
            # the partOf property of the fhir location object representing this room
            department_id = self.rooms[room_id].get_partOf_reference()
            if department_id:
                if department_id in self.departments:
                    self.department_rooms[department_id] = RoomReference(id=room_id) #self.rooms[room_id]["fhir_location"].get_reference_object()

    def _match_departments_to_hospitals(self, hospital_stay: HospitalStay):
        for department_id in self.departments:
            hospital_id = self.departments[department_id].hospital_id

            if hospital_id in self.hospitals:
                
                if not hospital_id in self.hospital_stays:
                    # create hospital_stay object for this hospital if it does not already exist
                    self.hospital_stays[hospital_id] = hospital_stay # a HospitalStay object
                    self.hospital_stays[hospital_id].hospital = HospitalReference(id=hospital_id)
                    self.department_stays[hospital_id] = []

                # append department stays for a created/existing hospital stay
                hs = self.hospital_stays[hospital_id] # HospitalStay
                ds = self.departments[department_id] # DepartmentStay
                room = self.department_rooms.get(department_id, None) #RoomReference

                ds_location = DeparmentStayLocation(data={
                    "hospital": HospitalReference(id=hospital_id),
                    "venue": HospitalReference(id=hospital_id),
                    "department": DeparmentReference(id=department_id), #self.departments[department_id]['fhir_location'].get_reference_object(),
                    "room": room,
                    "bed": self.room_beds[room.id] if room is not None and room.id in self.room_beds else None
                })

                self.department_stays[hospital_id].append(DeparmentStay(data={
                    "id": f"{hs.id}-{department_id}",
                    "hospital_stay": HospitalStayReference(id=hospital_stay.id), # HospitalStayReference object
                    "version": None,
                    "location": ds_location,
                    "starts_at": ds.period.get("start", None),
                }))

    def _get_adt_message(self):
        ret = []
        for hospital_id in self.hospital_stays:
            print(self.hospital_stays[hospital_id].hospital)
            ret.append({
                "hospital": model_to_dict(self.hospital_stays[hospital_id].hospital),
                "patient": model_to_dict(self.patient),
                "hospital_stay": model_to_dict(self.hospital_stays[hospital_id]),
                "department_stays": model_to_dict(self.department_stays[hospital_id], is_lsit=True)
            })
        return ret

    @staticmethod
    def read_test_data():
        try:
            return cache_get('encounters')
        except:
            return None
        
    @staticmethod
    def read_patient_test_data(patient_id):
        try:
            return cache_get(f"patient-encounters-{patient_id}")
        except:
            return None
