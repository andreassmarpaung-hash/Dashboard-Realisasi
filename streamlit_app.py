"""
Main entry point for Streamlit dashboard with error handling.
Imports dashboard module and catches any initialization errors.
"""
import sys
import os
import streamlit as st

# Verify environment setup
try:
    st.set_page_config(
        page_title="Dashboard Realisasi Belanja",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Show startup status
    st.write("🔄 Loading dashboard...")
    
    # Import dashboard module
    import dashboard
    
except FileNotFoundError as e:
    st.error(f"""
    ❌ **File Not Found Error**
    
    {str(e)}
    
    **Solution:** Ensure 'Belanja_Full_Baru.csv' is in the repository root.
    """)
    st.stop()
    
except Exception as e:
    st.error(f"""
    ❌ **Error Loading Dashboard**
    
    **Details:** {str(e)}
    
    **Working Directory:** {os.getcwd()}
    **Files Here:** {', '.join(os.listdir('.')[:10])}
    
    Check Streamlit Cloud logs for more information.
    """)
    st.stop()
