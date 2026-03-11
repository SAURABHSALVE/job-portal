from datetime import datetime
from gmail_reader import GmailReader

class ReminderService:
    """
    Checks the sheets_manager for applications that need to be followed up 
    on today's date, and uses the gmail_reader to email the user a nice summary.
    """
    def __init__(self, sheets_manager, gmail_reader: GmailReader):
        self.sheets_manager = sheets_manager
        self.gmail_reader = gmail_reader
        
    def check_and_send_reminders(self, user_email):
        """
        Sends an email reminder about any job applications that need follow-up.
        """
        today_date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Pull records that match today's date and aren't Rejected or Offered
        follow_ups = self.sheets_manager.get_applications_for_followup(today_date_str)
        
        if not follow_ups:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No follow-ups needed for {today_date_str}.")
            return
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Follow-ups needed for {len(follow_ups)} applications. Sending email.")
        
        # Build our email body
        body = f"Hello!\n\nYou have {len(follow_ups)} job applications to follow up on today ({today_date_str}):\n\n"
        
        for app in follow_ups:
            body += f"- Company: {app.get('Company')}\n"
            body += f"  Role: {app.get('Role')}\n"
            body += f"  Platform: {app.get('Platform')}\n"
            body += f"  Applied On: {app.get('Date Applied')}\n"
            body += "-" * 30 + "\n"
            
        body += "\nGood luck!"
        
        subject = f"🔔 Job Follow-Up Reminder for {today_date_str}"
        self.gmail_reader.send_email(to=user_email, subject=subject, body=body)
        print("Sent reminder email.")
