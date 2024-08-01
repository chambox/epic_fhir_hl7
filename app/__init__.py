from flask import Flask, send_from_directory,redirect, url_for
from flask_swagger_ui import get_swaggerui_blueprint
from app.api.patient import api as patient_ns
from app.api.encounter import api as encounter_ns
from app.api.location import api as location_ns
from app.api.organization import api as organisation_ns
from app.api.careplan import api as careplan_ns
from flask_restx import Api
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    # Get the Swagger URL and API URL from environment variables
    SWAGGER_URL = os.getenv('SWAGGER_URL', '/api/docs')  # URL for exposing Swagger UI
    API_URL = os.getenv('API_URL', '/docs/openapi.yaml')  # URL for the OpenAPI YAML file
    
  
    # Swagger UI setup
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,  # Swagger UI endpoint
        API_URL,  # OpenAPI YAML file endpoint
        config={  # Swagger UI configuration options
            'app_name': "Integrating TNT with EPIC FHIR API"
        }
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Create API
    api = Api(
        app, 
        version='1.0', 
        title='EPIC FHIR  TNT integration API',
        description='A simple API to integrate EPIC FHIR with TNT'
    )

    # add namespaces
    api.add_namespace(patient_ns, path='/patient')
    api.add_namespace(encounter_ns, path='/encounter')
    api.add_namespace(location_ns, path='/location')
    api.add_namespace(organisation_ns,path='/organisation')
    api.add_namespace(careplan_ns, path='/careplan')
    
    # Serve the OpenAPI YAML file
    @app.route(API_URL)
    def get_openapi_yaml():
        return send_from_directory(os.path.join(app.root_path, 'docs'), 'openapi.yaml')

   # Root route to redirect to Swagger UI
    @app.route('/')
    def index():
        return redirect(SWAGGER_URL)

    return app
