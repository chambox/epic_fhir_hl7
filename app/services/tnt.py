from flask import current_app as app
import requests
from config import Config
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler("tnt_service.log")
file_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Add a stream handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


<<<<<<< HEAD

=======
>>>>>>> 5a86c0f (Code formatting)
class TnTService(object):
    def post_adt_message(self, json_request):
        url = Config.TNT_RECEIVE_ENDPOINT
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.TNT_ACCESS_TOKEN}",
        }

        response = requests.post(url, headers=headers, json=json_request)
        logger.info(f"Response from TNT: {response.status_code} - {response.text}")
        if response.status_code > 204:
            raise TnTServiceException(
                response.content.decode("utf-8"), response.status_code
            )
<<<<<<< HEAD
=======

        logger.info(f"Request payload: {json_request}")
>>>>>>> 5a86c0f (Code formatting)
        return response


class TnTServiceException(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {"error": self.message}
