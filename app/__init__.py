from flask import Flask
from app.docs import doc_bp, SWAGGER_URL
from app.api import api


def create_app():
    app = Flask(__name__)

    # Initialize api with app
    api.init_app(app)

    # Add documentation (swagger blueprint)
    app.register_blueprint(doc_bp, url_prefix=SWAGGER_URL)

    return app
