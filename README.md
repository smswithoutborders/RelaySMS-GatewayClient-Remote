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

### Running the Application

1. **Start the Application**:

   ```bash
   GATEWAY_SERVER_HOST= \
   GATEWAY_SERVER_PORT= \
   PORT= \
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
