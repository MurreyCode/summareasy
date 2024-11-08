import os
import base64
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

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
        print('Messages:')
        email_data = {}
        for message in messages[:5]:  # Limit to first 5 messages
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data[msg['snippet']] = msg['payload']['headers']
            print(f"Snippet: {msg['snippet']}")
            print(f"Email Headers: {json.dumps(msg['payload']['headers'], indent=2)}")
            
        return email_data

def main():
    """Main function to authenticate and retrieve emails."""
    service = authenticate()
    emails = get_emails(service)
    print("Fetched email data:", emails)

if __name__ == '__main__':
    main()
