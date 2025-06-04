"""Flask Application."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from flask import Flask, request, Blueprint, jsonify
import requests
from twilio.twiml.messaging_response import MessagingResponse
from utils import get_configs

app = Flask(__name__)

GATEWAY_SERVER_HOST = get_configs("GATEWAY_SERVER_HOST", strict=True)
GATEWAY_SERVER_PORT = get_configs("GATEWAY_SERVER_PORT", strict=True)
PORT = get_configs("PORT", default_value=7000)

api_bp_v1 = Blueprint("api", __name__, url_prefix="/v1")

gateway_server_urls = (f"{GATEWAY_SERVER_HOST}:{GATEWAY_SERVER_PORT}/v3/publish",)


def gateway_server_request(url, payload):
    """
    Send a POST request to the specified gateway server URL.

    Args:
        url (str): The URL to send the request to.
        payload (dict): The payload to send in the request.

    Returns:
        requests.Response: The response from the server.
    """
    try:
        response = requests.post(url, json=payload, timeout=10)
        app.logger.info(
            "Response from Gateway Server (%s): %s -- %s",
            url,
            response.status_code,
            response.text,
        )
        return response
    except requests.RequestException as e:
        app.logger.error("Failed to send request to %s: %s", url, e)
        return None


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

        publish_payload = {
            "address": data["From"],
            "text": data["Body"],
            "date": str(int(datetime.now().timestamp())),
            "date_sent": str(int(datetime.now().timestamp())),
        }

        with ThreadPoolExecutor(max_workers=len(gateway_server_urls)) as executor:
            executor.map(
                lambda url: gateway_server_request(url, publish_payload),
                gateway_server_urls,
            )

        return str(resp)

    except Exception as e:
        app.logger.exception("Error processing incoming Twilio SMS: %s", e)
        return (
            jsonify({"error": "Oops! Something went wrong. Please try again later."}),
            500,
        )


app.register_blueprint(api_bp_v1)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
