import streamlit as st
import pandas as pd
import numpy as np
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import io

# Set page title
st.set_page_config(page_title="Data Profiling App", layout="wide")
st.title("Advanced Data Profiling")
st.markdown("Upload a CSV file to generate a comprehensive profile report.")

# Sidebar configuration
st.sidebar.header("Configuration Options")
exploration_mode = st.sidebar.radio("Profiling Mode", ["Minimal", "Exploratory"])
sample_data = st.sidebar.checkbox("Sample data for large files", True)
max_sample = st.sidebar.number_input("Max rows to sample (if sampling)", 
                                     min_value=1000, max_value=100000, value=10000, step=1000)
delimiter_option = st.sidebar.selectbox("CSV Delimiter", [",", ";", "\t", "|", "Other"])
if delimiter_option == "Other":
    custom_delimiter = st.sidebar.text_input("Enter custom delimiter", "")
    delimiter = custom_delimiter if custom_delimiter else ","
else:
    delimiter = delimiter_option

# Main content
upload_file = st.file_uploader("Upload your data file", type=["csv", "txt"])

if upload_file is not None:
    try:
        file_details = {"Filename": upload_file.name, "FileType": upload_file.type, "FileSize": f"{upload_file.size / 1024:.2f} KB"}
        st.write("File Details:", file_details)
        
        # Read file with appropriate delimiter
        with st.spinner("Reading data..."):
            try:
                df = pd.read_csv(upload_file, delimiter=delimiter)
            except Exception as e:
                st.error(f"Error reading CSV with delimiter '{delimiter}': {e}")
                try:
                    # Fall back to pandas auto-detection
                    upload_file.seek(0)  # Reset file pointer
                    df = pd.read_csv(upload_file, sep=None, engine='python')
                    st.warning("Used auto-detection for delimiter.")
                except Exception as e2:
                    st.error(f"Failed to read file: {e2}")
                    st.stop()
        
        # Display data preview with option to show more
        with st.expander("Data Preview", expanded=True):
            st.dataframe(df.head(10))
            st.text(f"Dataset Shape: {df.shape[0]} rows and {df.shape[1]} columns")
        
        # If df is empty, show error
        if df.empty:
            st.error("Dataset is empty!")
            st.stop()
            
        # Sample data if needed
        if sample_data and len(df) > max_sample:
            st.info(f"Dataset is large ({len(df)} rows). Sampling {max_sample} rows for faster processing.")
            df = df.sample(n=max_sample, random_state=42)
            
        # Generate profile report based on selected mode
        with st.spinner("Generating profile report, this may take a while..."):
            profile_config = {
                "explorative": True if exploration_mode == "Exploratory" else False,
                "minimal": True if exploration_mode == "Minimal" else False,
                "title": f"Profiling Report for {upload_file.name}"
            }
            
            # Create profile report
            pr = ProfileReport(df, **profile_config)
            
            # Display the report
            st.subheader("Data Profiling Report")
            st_profile_report(pr)
            
            # Export options
            export_format = st.selectbox("Export Report Format", ["", "HTML", "JSON"])
            if export_format:
                if export_format == "HTML":
                    report_html = pr.to_html()
                    st.download_button("Download HTML Report", report_html, file_name="profile_report.html")
                elif export_format == "JSON":
                    report_json = pr.to_json()
                    st.download_button("Download JSON Report", report_json, file_name="profile_report.json")
    
    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")
else:
    # Show instructions when no file is uploaded
    st.info("Please upload a CSV or TXT file to generate a profiling report.")
    
    # Example section
    with st.expander("About Data Profiling"):
        st.markdown("""
        This app uses `ydata_profiling` (formerly pandas-profiling) to generate comprehensive reports from your data, including:
        - Basic statistics
        - Correlations and relationships
        - Missing values analysis
        - Distribution visualization
        - Anomaly detection
        
        The **Minimal** mode is faster but provides less detail, while the **Exploratory** mode performs deeper analysis.
        """)
