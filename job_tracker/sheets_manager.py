import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import gspread

from config import (
    SCOPES, 
    SPREADSHEET_ID, 
    JOB_APPLICATIONS_SHEET, 
    FREELANCE_PROPOSALS_SHEET
)

def get_credentials():
    """
    Handles Gmail & Sheets API authentication.
    Prompts the user to log in on the first run, 
    and saves/refreshes a 'token.pickle' file for subsequent runs.
    """
    creds = None
    # We use a pickle file to store the credentials when we successfully authenticate
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If no valid token found, we authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Requires `credentials.json` from the Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

class SheetsManager:
    """
    Handles saving extracted job applications and freelance proposals
    to Google Sheets, and checking for follow ups.
    """
    def __init__(self, creds):
        # Authorize gspread with the oauth2 credentials
        self.gc = gspread.authorize(creds)
        
        # Connect to the specific spreadsheet setup in config.py
        self.spreadsheet = self.gc.open_by_key(SPREADSHEET_ID)
        self.ensure_sheets_exist()
        
    def ensure_sheets_exist(self):
        """Creates the necessary sheets and headers if they're missing."""
        # Setup Job Applications sheet
        try:
            job_sheet = self.spreadsheet.worksheet(JOB_APPLICATIONS_SHEET)
        except gspread.exceptions.WorksheetNotFound:
            job_sheet = self.spreadsheet.add_worksheet(title=JOB_APPLICATIONS_SHEET, rows="100", cols="20")
            headers = ["Company", "Role", "Platform", "Date Applied", "Follow Up Date", "Status", "Job Link", "Notes"]
            job_sheet.append_row(headers)
            
        # Setup Freelance Proposals sheet
        try:
            freelance_sheet = self.spreadsheet.worksheet(FREELANCE_PROPOSALS_SHEET)
        except gspread.exceptions.WorksheetNotFound:
            freelance_sheet = self.spreadsheet.add_worksheet(title=FREELANCE_PROPOSALS_SHEET, rows="100", cols="20")
            headers = ["Client", "Platform", "Proposal Date", "Budget", "Status", "Notes"]
            freelance_sheet.append_row(headers)

    def add_job_application(self, data):
        """Appends a new job application row."""
        sheet = self.spreadsheet.worksheet(JOB_APPLICATIONS_SHEET)
        # Note: Order matters, must match headers
        sheet.append_row([
            data.get('Company', ''),
            data.get('Role', ''),
            data.get('Platform', ''),
            data.get('Date Applied', ''),
            data.get('Follow Up Date', ''),
            data.get('Status', 'Applied'),
            data.get('Job Link', ''),
            data.get('Notes', '')
        ])

    def add_freelance_proposal(self, data):
        """Appends a new freelance proposal row."""
        sheet = self.spreadsheet.worksheet(FREELANCE_PROPOSALS_SHEET)
        sheet.append_row([
            data.get('Client', ''),
            data.get('Platform', ''),
            data.get('Proposal Date', ''),
            data.get('Budget', 'Unknown'),
            data.get('Status', 'Applied'),
            data.get('Notes', '')
        ])
        
    def get_applications_for_followup(self, today_date_str):
        """Returns rows that need follow-up action today."""
        sheet = self.spreadsheet.worksheet(JOB_APPLICATIONS_SHEET)
        records = sheet.get_all_records()
        
        follow_ups = []
        for row in records:
            # Use 'Follow Up Date' column string comparison
            if row.get('Follow Up Date') == today_date_str:
                if row.get('Status') not in ['Rejected', 'Offer']:
                    follow_ups.append(row)
                    
        return follow_ups
