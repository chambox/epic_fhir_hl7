from flask import Blueprint
from .views import PatientAggregateData

api_blueprint = Blueprint('api', __name__)
api_blueprint.add_url_rule('/patient/<string:patient_id>', view_func=PatientAggregateData.as_view('patient_aggregate_data'))
