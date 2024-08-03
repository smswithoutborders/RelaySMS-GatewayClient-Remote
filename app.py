"""Flask Application."""

from flask import Flask, request, Blueprint, jsonify
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

        if not data.get("From"):
            app.logger.error("Missing required field: 'From'")
            return jsonify({"error": "Missing required field: 'From'"}), 400

        if not data.get("Body"):
            app.logger.error("Missing required field: 'Body'")
            return jsonify({"error": "Missing required field: 'Body'"}), 400

        publish_payload = {"address": data["From"], "text": data["Body"]}
        gateway_server_url = (
            f"{GATEWAY_SERVER_HOST}:{GATEWAY_SERVER_PORT}/sms/platform/twilio"
        )
        response = requests.post(gateway_server_url, json=publish_payload, timeout=10)
        app.logger.info(
            "Response from Gateway Server: %s -- %s",
            response.status_code,
            response.text,
        )

        return str(resp)

    except Exception as e:
        app.logger.exception("Error processing incoming twilio sms: %s", e)
        return (
            jsonify({"error": "Oops! Something went wrong. Please try again later."}),
            500,
        )


app.register_blueprint(api_bp_v1)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
