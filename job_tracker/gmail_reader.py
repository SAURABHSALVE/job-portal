import base64
import re
from datetime import datetime
from email.message import EmailMessage
from googleapiclient.discovery import build

class GmailReader:
    """
    Handles interacting with the Gmail API. 
    Can fetch unread messages, parse their text content, and extract basic job details.
    """
    def __init__(self, creds):
        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_unread_messages(self, max_results=10):
        """
        Fetches unread application-related messages from the user's inbox based on 
        specific keywords, and extracts company and role information.
        """
        # Specific search string based on user's requirements
        search_query = 'is:unread ("application received" OR "thanks for applying" OR "application submitted")'
        
        results = self.service.users().messages().list(userId='me', q=search_query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        extracted_applications = []
        for msg in messages:
            msg_id = msg['id']
            # Fetch the full email
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            # Extract basic parts of the email
            headers = message['payload'].get('headers', [])
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'No Sender')
            body = self._get_email_body(message['payload'])
            
            # Extract the specific details specified in requirements
            company = self._extract_company(sender, subject)
            role = self._extract_role(subject, body)
            platform = self._extract_platform(sender, subject, body)
            
            # Use today as the date applied, follow up in 5 days
            date_applied_obj = datetime.now()
            date_applied = date_applied_obj.strftime("%Y-%m-%d")
            from datetime import timedelta
            follow_up_date = (date_applied_obj + timedelta(days=5)).strftime("%Y-%m-%d")
            
            # Try to grab a link to the job from the body
            job_link = self._extract_link(body)

            # Creating the requested dictionary structure
            application_data = {
                'company': company,
                'role': role,
                'platform': platform,
                'date_applied': date_applied,
                'follow_up_date': follow_up_date,
                'job_link': job_link,
                'email_id': msg_id  # Keeping this internally to mark as read later
            }
            
            extracted_applications.append(application_data)
            
        return extracted_applications

    def _extract_company(self, sender, subject):
        """Finds the company name from the email subject or sender domain."""
        subject = subject.strip()
        
        # 1. "Application received by TestCompany for Software Engineer"
        match = re.search(r"received by\s+([^f]+?)\s+for", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 2. "Your application was sent to [Company]"
        match = re.search(r"application was sent to\s+(.+)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 3. "Your application to [Role] at [Company]"
        match = re.search(r"\s+at\s+(.+)$", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 4. "Your application was viewed by [Company]"
        match = re.search(r"viewed by\s+(.+)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 5. "Update on Your Application - [Company]"
        match = re.search(r"-\s*([^-\n]+)$", subject, flags=re.IGNORECASE)
        if match and "update" not in match.group(1).lower() and "application" not in match.group(1).lower():
            return match.group(1).strip()
            
        # 6. "Application to [Company] successfully submitted"
        match = re.search(r"Application to\s+([^\s]+)\s+successfully", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 7. Extracting from Sender Name (e.g. "Company Name <info@company.com>")
        sender_match = re.match(r"([^<]+)\s*<", sender)
        if sender_match:
            name = sender_match.group(1).strip().replace('"', '')
            if name.lower() not in ['linkedin', 'indeed', 'wellfound', 'glassdoor', 'upwork', 'fiverr', 'internshala', 'update']:
                return name
                
        # 8. Fallback: Parse the domain itself
        domain = sender.split('@')[-1].split('.')[0].capitalize()
        # If the domain is a default mailer or platform it isn't the company name
        if domain.lower() in ['gmail', 'yahoo', 'outlook', 'linkedin', 'indeed', 'wellfound', 'internshala']:
            match = re.search(r"^([^:]+):", subject)
            if match and "fwd" not in match.group(1).lower() and "update" not in match.group(1).lower() and "application" not in match.group(1).lower():
                return match.group(1).strip()
            return "Unknown Company"
            
        return domain

    def _extract_role(self, subject, body):
        """Finds the job role from the subject or body."""
        subject = subject.strip()
        
        # 1. "Application received by TestCompany for [Role]"
        match = re.search(r"for\s+(.+)$", subject, flags=re.IGNORECASE)
        if match and "position" not in match.group(1).lower():
            return match.group(1).split('-')[0].strip()
            
        # 2. "for the position of [Role] at"
        match = re.search(r"position of\s+(.+?)(?:\s+at|\s+in|\s+-|$)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 3. "Indeed Application: [Role]"
        match = re.search(r"Indeed Application:\s+(.+)$", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 4. "Your application to [Role] at"
        match = re.search(r"application to\s+(.+?)\s+at", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 5. "your application status for [Role] - India"
        match = re.search(r"status for\s+(.+?)(?:\s+-|$)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 6. "Job Application for [Role] is complete!"
        match = re.search(r"Application for\s+(.+?)(?:\s+received|\s+is complete|$)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try the email body
        match_body = re.search(r"role of\s+([A-Za-z\s]+)\b", body, flags=re.IGNORECASE)
        if match_body:
            return match_body.group(1).strip()
            
        return "Unknown Role"

    def _extract_platform(self, sender, subject, body):
        """Detects if it came from LinkedIn, Indeed, etc."""
        text = f"{sender} {subject} {body}".lower()
        for p in ["linkedin", "indeed", "glassdoor", "internshala", "wellfound", "upwork", "fiverr"]:
            if p in text:
                return p.capitalize()
        return "Direct"

    def _extract_link(self, body):
        """Attempts to find an http job link in the text."""
        # Use regex to find http/https links
        match = re.search(r"(https?://[^\s]+)", body)
        if match:
            return match.group(1).strip().strip('">')
        return ""

    def _get_email_body(self, payload):
        """Recursively parses the MIME text structure to plain text."""
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
        """Removes the UNREAD label so it doesn't get processed twice."""
        self.service.users().messages().modify(
            userId='me', 
            id=msg_id, 
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

    def send_email(self, to, subject, body):
        """Sends an email (for daily reminders)."""
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        self.service.users().messages().send(userId="me", body=create_message).execute()
