from flask import Flask, send_from_directory, redirect, url_for, current_app as app
from flask_swagger_ui import get_swaggerui_blueprint
import os

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get the Swagger URL and API URL from environment variables
SWAGGER_URL = os.getenv("SWAGGER_URL", "/docs")  # URL for exposing Swagger UI
YAML_API_URL = os.getenv(
    "YAML_YAML_API_URL", "/openapi.yaml"
)  # URL for the OpenAPI YAML file

# Swagger UI setup
doc_bp = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI endpoint
    SWAGGER_URL + YAML_API_URL,  # OpenAPI YAML file endpoint
    config={  # Swagger UI configuration options
        "app_name": "Integrating TNT with EPIC FHIR API"
    },
)


@doc_bp.route(YAML_API_URL)
def get_openapi_yaml():
    return send_from_directory(os.path.join(app.root_path, "docs"), "openapi.yaml")
