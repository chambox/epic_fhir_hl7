from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from app.services.fhir_service import FhirService, FhirServiceAuthenticationException, FhirServiceApiException

api = Namespace("patient", description="Patient related operations")

# Define DepartmentStay model
bed_reference_model = api.model('BedReference', {
    "id": fields.String(required=True, description="The Bed Identifier")
})

room_reference_model = api.model('RoomReference', {
    "id": fields.String(required=True, description="The Room Identifier")
})

department_reference_model = api.model('DepartmentReference', {
    "id": fields.String(required=True, description="The Department Identifier")
})

venue_reference_model = api.model('VenueReference', {
    "id": fields.String(required=True, description="The Venue Identifier")
})

hospital_reference_model = api.model('HospitalReference', {
    "id": fields.String(required=True, description="The Hospital Identifier")
})

location_model = api.model('Location', {
    "hospital": fields.Nested(hospital_reference_model, required=True, description="Hospital Reference"),
    "venue": fields.Nested(venue_reference_model, required=True, description="Venue Reference"),
    "department": fields.Nested(department_reference_model, required=True, description="Department Reference"),
    "room": fields.Nested(room_reference_model, required=True, description="Room Reference"),
    "bed": fields.Nested(bed_reference_model, required=True, description="Bed Reference"),
})

department_stay_model = api.model('DepartmentStay', {
    "id": fields.String(required=True, description="The DepartmentStay Identifier"),
    "hospital_stay": fields.Nested(api.model('HospitalStayReference', {
        "id": fields.String(required=True, description="Hospital Stay Identifier")
    }), required=True, description="HospitalStay Reference"),
    "version": fields.String(required=True, description="Version ID"),
    "location": fields.Nested(location_model, required=True, description="Location Details"),
    "starts_at": fields.String(required=True, description="Start Date/Time")
})

# Define HospitalStay model
hospital_stay_model = api.model('HospitalStay', {
    "id": fields.String(required=True, description="The Encounter Identifier"),
    "version": fields.String(required=True, description="Version ID"),
    "patient": fields.Raw(required=True, description="Patient Reference"),
    "hospital": fields.Nested(hospital_reference_model, required=True, description="Hospital Reference"),
    "from_at": fields.String(required=True, description="Start Date/Time"),
    "until_at": fields.String(required=True, description="End Date/Time"),
    "is_pre_discharge": fields.Boolean(required=True, description="Pre Discharge Status"),
    "is_pre_admission": fields.Boolean(required=True, description="Pre Admission Status"),
    "reason_of_admission": fields.String(required=True, description="Reason of Admission"),
    "reason_of_discharge": fields.String(required=True, description="Reason of Discharge"),
    "department_stays": fields.List(fields.Nested(department_stay_model), required=True, description="List of Department Stays")
})

# Define PatientData model
patient_data_model = api.model('PatientData', {
    "patient": fields.Raw(required=True, description="Patient Data as returned from the EPIC /Patient endpoint"),
    "hospital_stay": fields.List(fields.Nested(hospital_stay_model), required=False, description="Hospital Stay Data")
})

# Define Patient model
patient = api.model(
    "Patient",
    {
        "id": fields.String(required=True, description="The Patient Identifier"),
        "data": fields.Nested(patient_data_model, required=False, description="EPIC Data"),
    },
)

# Define PatientList model
patient_list_model = api.model('PatientList', {
    'totalCount': fields.Integer(description='Total number of items'),
    'items': fields.List(fields.Nested(patient), description='List of items')
})

# Sample patient data
PATIENTS = [
    {"id": "erXuFYUfucBZaryVksYEcMg3"},
    {"id": "eq081-VQEgP8drUUqCWzHfw3"},
    {"id": "eAB3mDIBBcyUKviyzrxsnAw3"},
    {"id": "egqBHVfQlt4Bw3XGXoxVxHg3"},
    {"id": "eIXesllypH3M9tAA5WdJftQ3"}
]

@api.route("/list")
class PatientList(Resource):
    @api.doc("list_patients")
    @api.marshal_list_with(patient_list_model)
    def get(self):
        """List of patients via HL7 with their Patient IDs"""
        return {
            "totalCount": len(PATIENTS),
            "items": PATIENTS
        }

@api.route("/<id>")
@api.param("id", "The Patient Identifier")
@api.response(404, "Patient not Found")
@api.response(500, "An unexpected error against the EPIC API")
class Patient(Resource):
    @api.doc("get_patient")
    @api.marshal_with(patient)
    def get(self, id):
        """Fetch a patient given its identifier"""
        try:
            fs = FhirService()
            return {
                "id": id,
                "data": fs.get_aggregate_patient_data(id)
            }
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), auth_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code
