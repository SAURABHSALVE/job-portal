import pickle
import os.path
import os
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import gspread
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# We need these scopes to read and write to Google Sheets and read Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/spreadsheets'
]

def get_credentials():
    """
    Handles logging into Google. 
    It will open a browser window the first time you run it.
    """
    creds = None
    # 'token.pickle' stores your login session so you don't have to log in every time
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no valid credentials, we ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You must have download credentials.json from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080, prompt='consent')
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
    return creds

class SheetsManager:
    """
    Connects to Google Sheets and manages our application rows.
    """
    def __init__(self, creds):
        # 1. Connect to Google Sheets using gspread
        self.client = gspread.authorize(creds)
        
        # 2. Open spreadsheet using the ID from .env
        if not SPREADSHEET_ID:
            print("Error: SPREADSHEET_ID not found in .env file.")
            raise ValueError("Missing SPREADSHEET_ID")
            
        try:
            self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Error: Could not find the spreadsheet with ID: {SPREADSHEET_ID}")
            print("Please ensure the spreadsheet ID is correct and you have access to it.")
            raise
            
        # Ensure the sheets exist
        self.job_sheet_name = 'Job Applications'
        self.freelance_sheet_name = 'Freelance Proposals'
        self.ensure_sheets_exist()

    def ensure_sheets_exist(self):
        """Creates the necessary sheets and headers if they're missing."""
        # Setup Job Applications sheet
        try:
            job_sheet = self.spreadsheet.worksheet(self.job_sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            job_sheet = self.spreadsheet.add_worksheet(title=self.job_sheet_name, rows="100", cols="20")
            headers = ["Company", "Role", "Platform", "Date Applied", "Follow Up Date", "Status", "Job Link", "Notes"]
            job_sheet.append_row(headers)
            
        # Setup Freelance Proposals sheet
        try:
            freelance_sheet = self.spreadsheet.worksheet(self.freelance_sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            freelance_sheet = self.spreadsheet.add_worksheet(title=self.freelance_sheet_name, rows="100", cols="20")
            headers = ["Client", "Platform", "Proposal Date", "Budget", "Status", "Notes"]
            freelance_sheet.append_row(headers)

    def add_job_application(self, data):
        """
        Appends a new job application row to the 'Job Applications' sheet.
        """
        # Open the correct sheet
        sheet = self.spreadsheet.worksheet(self.job_sheet_name)
        
        # We append a row matching our expected columns 
        # (Company, Role, Platform, Date Applied, Follow Up Date, Status, Job Link, Notes)
        row_to_add = [
            data.get('company', ''),
            data.get('role', ''),
            data.get('platform', ''),
            data.get('date_applied', ''),
            data.get('follow_up_date', ''), # Can be calculated here or passed in data
            data.get('status', 'Applied'),
            data.get('job_link', ''),
            data.get('notes', '')
        ]
        
        # Insert the new row directly at the top (under the headers at row 2)
        # This prevents it from appending to row 100+ if there are empty formatted rows above.
        sheet.insert_row(row_to_add, index=2)

    def add_freelance_proposal(self, data):
        """
        Appends a new freelance proposal row to the 'Freelance Proposals' sheet.
        """
        # Open the correct sheet
        sheet = self.spreadsheet.worksheet(self.freelance_sheet_name)
        
        # We append a row matching our expected freelance columns
        # (Client, Platform, Proposal Date, Budget, Status, Notes)
        row_to_add = [
            data.get('client', ''),
            data.get('platform', ''),
            data.get('proposal_date', ''),
            data.get('budget', 'Unknown'),
            data.get('status', 'Applied'),
            data.get('notes', '')
        ]
        
        # Insert the new row directly at the top (under the headers at row 2)
        sheet.insert_row(row_to_add, index=2)
        
    def get_applications_for_followup(self, today_date_str):
        """
        Reads the Job Applications sheet and returns rows where the 
        'Follow Up Date' matches today's date.
        """
        sheet = self.spreadsheet.worksheet(self.job_sheet_name)
        
        # Get all records as a list of dictionaries (keys are header row names)
        all_records = sheet.get_all_records()
        
        due_today = []
        for row in all_records:
            # Check if the 'Follow Up Date' column equals today's date
            if row.get('Follow Up Date', '') == today_date_str:
                due_today.append(row)
                
        return due_today
