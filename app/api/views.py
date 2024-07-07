from flask.views import MethodView
from flask import jsonify
from app.services.fhir_service import get_aggregate_patient_data

class PatientAggregateData(MethodView):
    def get(self, patient_id):
        data = get_aggregate_patient_data(patient_id)
        return jsonify(data)
