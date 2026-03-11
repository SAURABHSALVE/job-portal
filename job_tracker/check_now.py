import os
from dotenv import load_dotenv
import gspread
from sheets_manager import get_credentials

load_dotenv()
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

creds = get_credentials()
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID)

print("Title:", sheet.title)
for ws in sheet.worksheets():
    print(f"\n--- Tab: {ws.title} ---")
    rows = ws.get_all_values()
    print(f"Total rows: {len(rows)}")
    for i, row in enumerate(rows[:5]):
        print(f"Row {i+1}: {row}")
