def detect_platform(sender, subject, body):
    """
    Detects which platform (LinkedIn, Indeed, etc.) the application came from.
    We just search for the platform name in the email's sender, subject, and body.
    """
    # Combine text and lower case it to make searching easier
    text_to_search = f"{sender} {subject} {body}".lower()
    
    # List of platforms we are parsing
    platforms = [
        "linkedin", "indeed", "glassdoor", "internshala", 
        "wellfound", "upwork", "fiverr", "freelancer", "angel.co", "angellist"
    ]
    
    for platform in platforms:
        if platform in text_to_search:
            # Map aliases to standard names
            if platform in ['angel.co', 'angellist', 'wellfound']:
                return 'Wellfound'
            
            # Capitalize to match standard format
            return platform.capitalize()
            
    # If no platform was matched, we assume it's a direct email or unknown
    return "Unknown/Direct"
