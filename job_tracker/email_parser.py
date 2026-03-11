import re
from platform_detector import detect_platform
from datetime import datetime, timedelta

class EmailParser:
    """
    Parses application confirmation emails to extract useful details:
    Platform, Company/Client name, Role, etc.
    """
    def __init__(self):
        pass

    def parse_email(self, email_data):
        """
        Parses an email dictionary (from gmail_reader) and extracts application info.
        """
        sender = email_data['sender']
        subject = email_data['subject']
        body = email_data['body']
        date_str = email_data['date']
        
        # Use today's date for 'Date Applied'
        # In a real-world edge case, we could parse the standard email 'date_str'
        date_applied = datetime.now().strftime("%Y-%m-%d")
        
        # Follow up in 7 days by default
        follow_up_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        platform = detect_platform(sender, subject, body)
        
        # Assume Upwork, Fiverr, and Freelancer are freelance proposals
        is_freelance = platform in ['Upwork', 'Fiverr', 'Freelancer']
        
        company = self._extract_company(sender, subject, platform)
        role = self._extract_role(subject)
        
        if is_freelance:
            return {
                'type': 'freelance',
                'data': {
                    'Client': company,
                    'Platform': platform,
                    'Proposal Date': date_applied,
                    'Budget': 'Unknown',
                    'Status': 'Applied',
                    'Notes': f'Extracted from subject: {subject}'
                }
            }
        else:
            return {
                'type': 'job',
                'data': {
                    'Company': company,
                    'Role': role,
                    'Platform': platform,
                    'Date Applied': date_applied,
                    'Follow Up Date': follow_up_date,
                    'Status': 'Applied',
                    'Job Link': '',  # We don't extract the link yet, but can be added
                    'Notes': f'Extracted from subject: {subject}'
                }
            }
            
    def _extract_company(self, sender, subject, platform):
        """A simple heuristic function to get the company name from the email."""
        # e.g. "Application received by TechCorp"
        match = re.search(r"received by (.+?)(?:\.|$)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # e.g. "TechCorp: Application received"
        match = re.search(r"^(.+?):", subject)
        # Avoid picking up "Fwd:" or standard platform names
        if match and platform.lower() not in match.group(1).lower() and "fwd" not in match.group(1).lower():
            return match.group(1).strip()
            
        # Default fallback: extract from sender email domain
        domain = sender.split('@')[-1].split('.')[0].capitalize()
        # Clean standard mailers
        if domain in ['Gmail', 'Yahoo', 'Outlook']:
            return "Unknown Company"
        return domain

    def _extract_role(self, subject):
        """A simple heuristic function to extract the role from the subject."""
        # e.g. "Application for Software Engineer"
        match = re.search(r"for (?:the )?(?:position of )?(.+?)(?: at| in| -|$)", subject, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return "Unknown Role"
