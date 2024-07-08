from flask_restx import Api

from .patient import api as patient_api

api = Api(
    title="Data Fetch from EPIC",
    version="1.0",
    description="Fetch data from EPIC and transfer to TnT",
    prefix="/api"
)

api.add_namespace(patient_api)
