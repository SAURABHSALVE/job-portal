import base64
import os

def create_cloud_files():
    """Reads secrets from environments to build the required auth files."""
    if 'TOKEN_PICKLE_B64' in os.environ:
        with open('token.pickle', 'wb') as f:
            f.write(base64.b64decode(os.environ['TOKEN_PICKLE_B64']))

    if 'CREDENTIALS_JSON' in os.environ:
        with open('credentials.json', 'w') as f:
            f.write(os.environ['CREDENTIALS_JSON'])

# Build the files FIRST before any other imports load
create_cloud_files()

from sheets_manager import get_credentials, SheetsManager
from gmail_reader import GmailReader
from email_parser import EmailParser
from reminder_service import ReminderService
from main import process_emails, run_daily_reminders

def run_cloud():
    print("=== Starting Cloud Job Tracker ===")
    
    creds = get_credentials()
    sheets_manager = SheetsManager(creds)
    gmail_reader = GmailReader(creds)
    email_parser = EmailParser()
    reminder_service = ReminderService(sheets_manager, gmail_reader)
    
    profile = gmail_reader.service.users().getProfile(userId='me').execute()
    user_email = profile['emailAddress']
    
    # Check for new emails
    process_emails(gmail_reader, email_parser, sheets_manager)
    
    # Run reminders if the Github Action sent the flag
    if os.getenv('RUN_REMINDERS') == 'true':
        run_daily_reminders(reminder_service, user_email)

if __name__ == "__main__":
    run_cloud()
