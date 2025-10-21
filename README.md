# Gateway Client Remote

## Getting Started

### Prerequisites

Make sure you have Python 3.7 or higher installed on your system.

### Setting Up the Environment

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/smswithoutborders/gateway-client-remote.git
   cd gateway-client-remote
   ```

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**:

   ```bash
   . venv/bin/activate
   ```

4. **Install Requirements**:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

The application requires the following environment variables:

#### Required Variables

- `GATEWAY_SERVER_HOST`: The hostname of the gateway server
- `GATEWAY_SERVER_PORT`: The port of the gateway server

#### Optional Variables

- `PORT`: The port to run the application on (default: 7000)

#### SMTP Configuration (Optional)

- `SMTP_HOST`: SMTP server hostname (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: Username for SMTP authentication
- `SMTP_PASSWORD`: Password for SMTP authentication
- `SMTP_FROM_ADDRESS`: Email address to send from
- `SMTP_TO_ADDRESS`: Email address to send notifications to

### Running the Application

1. **Start the Application**:

   ```bash
   GATEWAY_SERVER_HOST=your_gateway_host \
   GATEWAY_SERVER_PORT=your_gateway_port \
   SMTP_HOST=smtp.gmail.com \
   SMTP_PORT=587 \
   SMTP_USERNAME=your_email@gmail.com \
   SMTP_PASSWORD=your_app_password \
   SMTP_FROM_ADDRESS=your_email@gmail.com \
   SMTP_TO_ADDRESS=notifications@yourdomain.com \
   PORT=7000 \
   python3 app.py
   ```

---

## API Documentation

### Twilio Callback Endpoint

**Endpoint**: `/v1/twilio-sms`

**Method**: `POST`

**Description**: Receives message from Twilio and forwards it to gateway server.

**Request**

- **Content-Type**: `application/x-www-form-urlencoded`
- **Body Parameters**: The endpoint expects data in the form of URL-encoded key-value pairs. Example parameters might include:
  - `From`: The sender's phone number.
  - `To`: The recipient's phone number.
  - `Body`: The content of the message.

**Example Request**:

```bash
curl -X POST "http://localhost:7000/v1/twilio-sms" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "From=+1234567890&To=+1234567890&Body=Hello%20World"
```
