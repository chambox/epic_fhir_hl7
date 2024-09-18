from flask import current_app as app, request
from flask_restx import Namespace, Resource, fields
from app.utils.hl7parser import hl7parser, hl7messageexception
from app.services.cron import CronService
from app.services.tnt import TnTService, TnTServiceException
from datetime import datetime
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add a file handler
file_handler = logging.FileHandler("adtmessage.log")
file_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)
api = Namespace("adtmessage", description="ADT Message Operations")

error_model = api.model("ErrorModel", {"error": fields.String(required=True)})


@api.route("/hl7")
@api.param("data", _in="body", contentType="text/plain", default="")
@api.response(400, "Bad Request", error_model)
class AdtMessage(Resource):
    @api.doc(
        """
        Receive an hl7 message and parse it, then use Patient ID to get encounters.
        The hl7 message is expected to be well formatted.

        Returns: JSON formatted ADT message (from patient encounters, fetched using patient ID)
    """
    )
    def post(self):
        """Receive raw ADT message, process it and return JSON formatted ADT message (from patient encounters, fetched using patient ID)"""
        try:
            # 1. Receive HL7 message
            hl7_message = request.data.decode("utf-8")
            if not hl7_message:
                return {"error": "ADT message is required"}, 400

            hl7_message = hl7_message.replace("\\n", "\n")
            hl7message = hl7parser.parse(hl7_message)

            pid_segment = hl7message.get_segment("PID")
            if not pid_segment:
                raise hl7messageexception("PID segment not found in the HL7 message")

            patient = hl7message.get_patient()

            # 2. Fetch data from EPIC
            encounters = CronService().parse_partient_encounters(patient["patient_id"])

            # 3. Loop over encounters and post each one
            responses = []
            for encounter in encounters:
                try:
                    json_request = {
                        "type": "adt",
                        "message_id": None,
                        "payload": encounter,
                        "message_created_at": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "sending_system_id": "None",
                    }
                    res = TnTService().post_adt_message(json_request=json_request)
                    responses.append(
                        {
                            "encounter_id": encounter.get("encounter_id"),
                            "status": "success",
                            "status_code": res.status_code,
                        }
                    )
                except TnTServiceException as e:
                    logger.error(
                        f"TnTServiceException occurred while posting encounter {encounter.get('encounter_id')}: {e}"
                    )
                    traceback.print_exc()
                    responses.append(
                        {
                            "encounter_id": encounter.get("encounter_id"),
                            "status": "failed",
                            "error": str(e),
                            "status_code": e.status_code,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Exception occurred while posting encounter {encounter.get('encounter_id')}: {e}"
                    )
                    traceback.print_exc()
                    responses.append(
                        {
                            "encounter_id": encounter.get("encounter_id"),
                            "status": "failed",
                            "error": str(e),
                            "status_code": 400,
                        }
                    )

            return {
                "success": f"Data for patient {patient['patient_id']} has been received and processed",
                "responses": responses,
            }, 200

        except TnTServiceException as e:
            logger.error(f"TnTServiceException occurred: {e}")
            traceback.print_exc()
            return e.to_dict(), e.status_code
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            traceback.print_exc()
            return {"error": str(e)}, 400
