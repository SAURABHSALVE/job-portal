import time
import schedule
from sheets_manager import get_credentials, SheetsManager
from gmail_reader import GmailReader
from email_parser import EmailParser
from reminder_service import ReminderService
from config import REMINDER_TIME_STR

def process_emails(gmail_reader, email_parser, sheets_manager):
    """
    Core function for polling emails and processing new applications.
    """
    print("Checking for new application emails...")
    emails = gmail_reader.fetch_unread_messages()
    
    if not emails:
        print("No new emails found.")
        return

    for app_data in emails:
        print(f"Processing email: '{app_data.get('company', 'Unknown')} - {app_data.get('role', 'Unknown')}'")
        
        # We process everything as a job application based on the new requirements structure
        sheets_manager.add_job_application({
            'company': app_data.get('company', ''),
            'role': app_data.get('role', ''),
            'platform': app_data.get('platform', ''),
            'date_applied': app_data.get('date_applied', ''),
            'follow_up_date': app_data.get('follow_up_date', ''),
            'job_link': app_data.get('job_link', '')
        })
        print(f"-> Added job application for {app_data.get('company', 'Unknown')}.")
        
        # Mark as read
        gmail_reader.mark_as_read(app_data['email_id'])

def run_daily_reminders(reminder_service, user_email):
    """
    Runs the check for any follow-up reminders.
    """
    print("Running daily reminder check...")
    reminder_service.check_and_send_reminders(user_email)

def main():
    print("=== Starting Automated Job & Freelance Application Tracker ===")
    
    # 1. Authorize user permissions to read email/sheets
    creds = get_credentials()
    
    # 2. Setup modules
    sheets_manager = SheetsManager(creds)
    gmail_reader = GmailReader(creds)
    email_parser = EmailParser()
    reminder_service = ReminderService(sheets_manager, gmail_reader)
    
    # We retrieve the actual email address tied to the oauth login
    # Because we'll email follow-up reminders to the user who authorized this app!
    profile = gmail_reader.service.users().getProfile(userId='me').execute()
    user_email = profile['emailAddress']
    print(f"Logged in and functioning as: {user_email}")
    
    # Run once at startup so we don't have to wait for the first scheduled run
    process_emails(gmail_reader, email_parser, sheets_manager)
    run_daily_reminders(reminder_service, user_email)

    # Schedule regular application checks (e.g. every hour)
    schedule.every(1).hours.do(process_emails, gmail_reader, email_parser, sheets_manager)
    
    # Schedule the daily digest email
    schedule.every().day.at(REMINDER_TIME_STR).do(run_daily_reminders, reminder_service, user_email)
    
    print(f"Scheduler is running. Checks occur every hour, reminders sent at {REMINDER_TIME_STR}.")
    print("Press Ctrl+C to exit.")
    
    # Infinite loop that runs pending scheduled tasks
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping Application Tracker...")

if __name__ == "__main__":
    main()
