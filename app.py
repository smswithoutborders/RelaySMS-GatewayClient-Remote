"""Flask Application."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, Blueprint, jsonify
import requests
from twilio.twiml.messaging_response import MessagingResponse
from utils import get_configs

app = Flask(__name__)

GATEWAY_SERVER_HOST = get_configs("GATEWAY_SERVER_HOST", strict=True)
GATEWAY_SERVER_PORT = get_configs("GATEWAY_SERVER_PORT", strict=True)
SMTP_HOST = get_configs("SMTP_HOST", default_value="smtp.gmail.com")
SMTP_PORT = int(get_configs("SMTP_PORT", default_value="587"))
SMTP_USERNAME = get_configs("SMTP_USERNAME")
SMTP_PASSWORD = get_configs("SMTP_PASSWORD")
SMTP_FROM_ADDRESS = get_configs("SMTP_FROM_ADDRESS")
SMTP_TO_ADDRESS = get_configs("SMTP_TO_ADDRESS")
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


def send_smtp_email(payload):
    """
    Send an email via SMTP containing SMS details.

    Args:
        payload (dict): The payload containing SMS details.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    if not all(
        [SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_ADDRESS, SMTP_TO_ADDRESS]
    ):
        app.logger.warning(
            "SMTP configuration incomplete. Skipping email notification."
        )
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM_ADDRESS
        msg["To"] = SMTP_TO_ADDRESS
        msg["Subject"] = "RelaySMS-Twilio Incoming SMS"

        email_body = json.dumps(payload, indent=4)
        msg.attach(MIMEText(email_body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        app.logger.info("Email sent successfully.")
        return True

    except Exception as e:
        app.logger.error("Failed to send email: %s", e)
        return False


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

        now_ms = int(datetime.now().timestamp() * 1000)
        publish_payload = {
            "address": data["From"],
            "text": data["Body"],
            "date": str(now_ms),
            "date_sent": str(now_ms),
        }

        with ThreadPoolExecutor(max_workers=len(gateway_server_urls) + 1) as executor:
            gateway_futures = [
                executor.submit(gateway_server_request, url, publish_payload)
                for url in gateway_server_urls
            ]

            smtp_future = executor.submit(send_smtp_email, publish_payload)

            for future in gateway_futures:
                try:
                    future.result(timeout=15)
                except Exception as e:
                    app.logger.error("Gateway server request failed: %s", e)

            try:
                smtp_future.result(timeout=15)
            except Exception as e:
                app.logger.error("SMTP email sending failed: %s", e)

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
