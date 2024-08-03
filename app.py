"""Flask Application."""

from flask import Flask, request, Blueprint
import requests
from twilio.twiml.messaging_response import MessagingResponse
from utils import get_configs

app = Flask(__name__)

GATEWAY_SERVER_HOST = get_configs("GATEWAY_SERVER_HOST", strict=True)
GATEWAY_SERVER_PORT = get_configs("GATEWAY_SERVER_PORT", strict=True)
PORT = get_configs("PORT", default_value=7000)

api_bp_v1 = Blueprint("api", __name__, url_prefix="/v1")


@api_bp_v1.route("/twilio-sms", methods=["GET", "POST"])
def twilio_incoming_sms():
    """
    Endpoint to handle incoming messages from Twilio.
    """
    resp = MessagingResponse()

    try:
        data = request.form.to_dict()
        app.logger.debug("Received data from Twilio: %s", data)
        gateway_server_url = (
            f"{GATEWAY_SERVER_HOST}:{GATEWAY_SERVER_PORT}/sms/platform/twilio"
        )
        response = requests.post(gateway_server_url, json=data, timeout=10)
        app.logger.debug("Response from Gateway Server: %s", response.json)

        return str(resp)

    except Exception as e:
        app.logger.exception("Error processing incoming twilio sms: %s", e)
        return str(resp)


app.register_blueprint(api_bp_v1)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
