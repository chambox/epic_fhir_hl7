from flask_restx import Namespace, Resource, fields

"""
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

"""
