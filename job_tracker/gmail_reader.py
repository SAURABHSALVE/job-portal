from googleapiclient.discovery import build
import base64
from email.message import EmailMessage

class GmailReader:
    """
    Handles interacting with the Gmail API. 
    Can fetch unread messages, parse their text content, and send emails (for reminders).
    """
    def __init__(self, creds):
        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_unread_messages(self, query=None):
        """
        Fetches unread application-related messages from the user's inbox.
        """
        if query is None:
            # A broad search query to find job application confirmations
            query = "is:unread (subject:\"application\" OR subject:\"applied\" OR subject:\"proposal\" OR subject:\"received\")"
            
        results = self.service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        email_data_list = []
        for msg in messages:
            msg_id = msg['id']
            # Fetch the full email payload
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            # Extract headers to get basic email info
            headers = message['payload'].get('headers', [])
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'No Sender')
            date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'No Date')
            
            # Extract plain text body
            body = self._get_email_body(message['payload'])
            
            email_data_list.append({
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            })
            
        return email_data_list

    def _get_email_body(self, payload):
        """
        Recursively extracts the plain text part of an email.
        """
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part.get('mimeType') == 'multipart/alternative':
                    return self._get_email_body(part)
        else:
            data = payload.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        return ""
        
    def mark_as_read(self, msg_id):
        """
        Removes the 'UNREAD' label from a specific message, 
        so we don't process it a second time.
        """
        self.service.users().messages().modify(
            userId='me', 
            id=msg_id, 
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

    def send_email(self, to, subject, body):
        """
        Sends an email (used for reminders).
        """
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject

        # Gmail API requires messages to be base64url encoded
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        self.service.users().messages().send(userId="me", body=create_message).execute()
