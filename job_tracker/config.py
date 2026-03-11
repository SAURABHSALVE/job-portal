import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google API Scopes needed for the project
# - Read & Modify Gmail messages (Modify is needed to remove UNREAD label)
# - Send Gmail messages (for reminders)
# - Read/Write Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Google Sheet settings
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', 'YOUR_SPREADSHEET_ID_HERE')

# Names of the sheets within the Google Spreadsheet
JOB_APPLICATIONS_SHEET = 'Job Applications'
FREELANCE_PROPOSALS_SHEET = 'Freelance Proposals'

# Reminder settings
REMINDER_TIME_STR = os.getenv('REMINDER_TIME', '09:00')
