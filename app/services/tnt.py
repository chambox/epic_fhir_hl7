from flask import current_app as app
import requests
from config import Config

class TnTService(object):

    def post_adt_message(self, json_request):
        url = Config.TNT_RECEIVE_ENDPOINT
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.TNT_ACCESS_TOKEN}"    
        }

        response = requests.post(url, headers=headers, json=json_request)
        print (response.status_code)
        if response.status_code > 204:
            raise TnTServiceException(response.content.decode('utf-8'), response.status_code)
        return response

class TnTServiceException(Exception):

    def __init__(self, message, status_code=400):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {"error": self.message}