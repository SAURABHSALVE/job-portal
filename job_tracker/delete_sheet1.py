import os
from dotenv import load_dotenv
import gspread
from sheets_manager import get_credentials

load_dotenv()
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

creds = get_credentials()
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID)

try:
    sheet1 = sheet.worksheet("Sheet1")
    sheet.del_worksheet(sheet1)
    print("Deleted 'Sheet1'. Now 'Job Applications' is the main visible sheet!")
except Exception as e:
    print("Sheet1 already deleted or not found:", e)
