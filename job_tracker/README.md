# Automated Job & Freelance Application Tracker

A Python-based personal automation system that reads unread Google Mail (Gmail) messages to automatically track sent job applications and freelance proposals across platforms, and stores them in Google Sheets. Includes a daily email reminder and an interactive Streamlit dashboard.

## Supported Platforms
- LinkedIn
- Indeed
- Glassdoor
- Internshala
- Wellfound
- Upwork
- Fiverr
- Freelancer

## Project Structure
- `config.py` - Core configuration settings (`.env` mapping).
- `gmail_reader.py` - Fetches and processes unread Gmail emails, and sends reminders.
- `platform_detector.py` - Infers platform names from emails using heuristics.
- `email_parser.py` - Extracts job/proposal details from email subject/body.
- `sheets_manager.py` - Appends extracted data to a Google Sheet and manages tabs.
- `reminder_service.py` - Analyzes Google Sheet jobs to send daily "Follow Up" emails.
- `main.py` - Connects everything. Scheduled to run continuously.
- `dashboard/streamlit_app.py` - Optional dashboard to view applications in a browser.

## Required Technologies
- Python 3.11
- Google Cloud Platform (for free API access)

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Google API Credentials
The project relies on OAuth 2.0 to access your Google account securely.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. In the sidebar, go to **APIs & Services > Library**, search for and **Enable** both:
   - Gmail API
   - Google Sheets API
4. Go to **APIs & Services > OAuth consent screen**:
   - Select **External** (or Internal if you have a Google Workspace).
   - Fill in your app name, support email, and developer contact info.
   - Add a Test user and enter your Google Email address.
5. Go to **APIs & Services > Credentials**:
   - Click **Create Credentials > OAuth client ID**.
   - Select **Desktop App** as the application type.
   - Create and download the JSON file. 
6. Rename the downloaded file to **`credentials.json`** and place it in the root folder (`job_tracker/credentials.json`).

*(Note: On the first run, Google will open a browser window asking you to log into your account and accept access. Since your app is not "verified", you might need to click "Advanced" -> "Go to app (unsafe)").*

### 3. Configure Google Sheets
1. Create a new empty Google Sheet (e.g. at [sheets.google.com](https://sheets.google.com)).
2. Look at the URL. It will look something like this:
   `https://docs.google.com/spreadsheets/d/1BxiMVs0XN5n68a9F0/edit`
3. The long random string (`1BxiMVs0XN5n68a9F0`) is your Spreadsheet ID.
4. Rename `.env.example` to `.env`.
5. Open `.env` and set `SPREADSHEET_ID=` to your spreadsheet ID.

### 4. Run the Tracker
Start the automated application tracker:

```bash
python main.py
```
*Note: Make sure to check the output of the console on initial run as Google expects you to login using the browser window that appears.*

### 5. Run the Interactive Dashboard
To visually see your applications through an interactive UI:

```bash
streamlit run dashboard/streamlit_app.py
```
