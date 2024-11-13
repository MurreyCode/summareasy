import os
import base64
import json
from datetime import datetime
from email import message_from_bytes
from email.header import decode_header

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from summareasy.data.models import Email

# If modifying the SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    """Authenticate and return the Gmail API service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_emails(service):
    """Fetch the emails from Gmail inbox."""
    # Call the Gmail API
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="newer_than:1d").execute()
    messages = results.get('messages', [])

    if not messages:
        print('No new messages found.')
    else:
        print(f'{len(messages)} messages retrieved.')
        raw_emails = {}
        for message in messages:
            message_id = message['id']
            message = service.users().messages().get(userId='me', id=message['id']).execute()
            raw_emails[message_id] = message['payload']
            
        return raw_emails


def process_emails(raw_emails) -> list[Email]:
    """Processes raw emails, decoding the body and extracting metadata."""

    def extract_header_value(headers, header_name):
        """Helper function to extract a specific header value."""
        for header in headers:
            if header['name'].lower() == header_name.lower():
                return header['value']
        return None

    processed_emails = []

    for email_id, email_payload in raw_emails.items():
        # Decode the email payload from base64
        decoded_bytes = base64.urlsafe_b64decode(email_payload['body']['data'])
        email_message = message_from_bytes(decoded_bytes)

        # Extract metadata
        headers = email_payload.get('headers', [])
        subject = extract_header_value(headers, 'Subject')
        sender = extract_header_value(headers, 'From')
        received_at = extract_header_value(headers, 'Date')

        if received_at:
            try:
                received_at = datetime.strptime(received_at, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                received_at = None

        # Extract the body content (plain text preferred, fallback to HTML)
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                try:
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode()
                        break  # Prefer plain text, skip others
                    elif content_type == "text/html" and not body:
                        body = part.get_payload(decode=True).decode()
                except Exception as e:
                    print(f"Error decoding email body: {e}")
        else:
            # If not multipart, get the payload directly
            body = email_message.get_payload(decode=True).decode()

        # Create a Pydantic model instance
        processed_email = Email(
            id=email_id,
            subject=subject,
            sender=sender,
            received_at=received_at,
            body=body,
            raw_email=email_payload
        )
        
        processed_emails.append(processed_email)

    return processed_emails


def main():
    """Main function to authenticate and retrieve emails."""
    service = authenticate()
    emails = {}
    raw_emails = get_emails(service)
    emails = process_emails(raw_emails)
    with open('emails.json', 'w') as file:
        json.dump(emails, file, indent=4)

if __name__ == '__main__':
    main()
