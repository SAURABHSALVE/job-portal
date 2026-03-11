import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import config and sheets_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_manager import get_credentials, SheetsManager
from config import JOB_APPLICATIONS_SHEET, FREELANCE_PROPOSALS_SHEET

st.set_page_config(page_title="Job Application Tracker", page_icon="📈", layout="wide")

st.title("📈 Job & Freelance Application Dashboard")
st.markdown("Monitor your job applications and freelance proposals tracked automatically from Gmail.")

@st.cache_data(ttl=600)  # Cache for 10 minutes to avoid hitting Google API limits
def load_data():
    try:
        creds = get_credentials()
        sheets_manager = SheetsManager(creds)
        
        # Pull data natively from the Google Spreadsheet
        job_sheet = sheets_manager.spreadsheet.worksheet(JOB_APPLICATIONS_SHEET)
        jobs_df = pd.DataFrame(job_sheet.get_all_records())
        
        free_sheet = sheets_manager.spreadsheet.worksheet(FREELANCE_PROPOSALS_SHEET)
        freelance_df = pd.DataFrame(free_sheet.get_all_records())
        
        return jobs_df, freelance_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

jobs_df, freelance_df = load_data()

# Navigation Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Job Applications", "Freelance Proposals"])

# Make sure we don't display a button unless data is available
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()

if page == "Overview":
    st.header("Activity Overview")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Job Applications", len(jobs_df) if not jobs_df.empty else 0)
    with col2:
        st.metric("Total Freelance Proposals", len(freelance_df) if not freelance_df.empty else 0)
        
    if not jobs_df.empty:
        st.subheader("Job Applications by Platform")
        platform_counts = jobs_df['Platform'].value_counts()
        st.bar_chart(platform_counts)

elif page == "Job Applications":
    st.header("Job Applications")
    if not jobs_df.empty:
        # Table filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(jobs_df['Status'].unique()))
        with col2:
            platform_filter = st.selectbox("Filter by Platform", ["All"] + list(jobs_df['Platform'].unique()))
            
        filtered_df = jobs_df
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        if platform_filter != "All":
            filtered_df = filtered_df[filtered_df['Platform'] == platform_filter]
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No job applications found yet.")

elif page == "Freelance Proposals":
    st.header("Freelance Proposals")
    if not freelance_df.empty:
        # Table filters
        platform_filter = st.selectbox("Filter by Platform", ["All"] + list(freelance_df['Platform'].unique()))
        
        if platform_filter != "All":
            filtered_df = freelance_df[freelance_df['Platform'] == platform_filter]
        else:
            filtered_df = freelance_df
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No freelance proposals found yet.")
