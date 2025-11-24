import streamlit as st
import requests
import os

# Default to localhost if not set, but in production this might change
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Personal Learning Assistant", layout="wide")

st.title("📚 Personal Learning Assistant")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Upload Curriculum", "Add Resource"])

# Health Check
with st.sidebar:
    st.divider()
    st.write("### System Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.success(f"Backend: {data['status']}")
            st.info(f"DB: {data.get('db', 'unknown')}")
        else:
            st.error(f"Backend Error: {response.status_code}")
    except Exception as e:
        st.error(f"Backend Offline")
        st.caption(f"Error: {str(e)}")

if page == "Dashboard":
    st.header("Dashboard")
    st.write("Welcome to your daily learning curator.")
    
    # Fetch all resources
    try:
        # We need to fetch all to filter locally or fetch two queries. Fetching all is fine for now.
        # Ensure we select the new columns
        res = requests.get(f"{API_URL}/resources").json()
        
        if res:
            import pandas as pd
            df = pd.DataFrame(res)
            
            # Ensure columns exist (handle old data if any)
            if "email_sent" not in df.columns:
                df["email_sent"] = False
            if "matched_topic" not in df.columns:
                df["matched_topic"] = None
                
            # Unread Resources (email_sent is False or None)
            unread_df = df[df["email_sent"] != True].copy()
            
            # Shared Resources (email_sent is True)
            shared_df = df[df["email_sent"] == True].copy()
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Unread Resources", len(unread_df))
            with col2:
                st.metric("Emails Sent", len(shared_df))
            with col3:
                st.metric("Total Resources", len(df))

            st.divider()
            
            # Table 1: Unread Resources
            st.subheader("📥 Unread Resources")
            if not unread_df.empty:
                # Select relevant columns
                display_unread = unread_df[["title", "type", "created_at", "url"]].copy()
                st.dataframe(display_unread, use_container_width=True)
                
                # Action to trigger email for unread
                st.caption("Select a resource to trigger an email manually:")
                resource_to_trigger = st.selectbox("Select Resource", unread_df["title"].tolist(), key="trigger_select")
                if st.button("Trigger Email Now"):
                    # Find ID
                    res_id = unread_df[unread_df["title"] == resource_to_trigger].iloc[0]["id"]
                    with st.spinner("Generating Email..."):
                        trigger_res = requests.post(f"{API_URL}/trigger-email", params={"resource_id": int(res_id)})
                        if trigger_res.status_code == 200:
                            data = trigger_res.json()
                            if data.get("status") == "success":
                                st.success("Email Generated & Sent!")
                                st.rerun() # Refresh to move to shared table
                            else:
                                st.info(data.get("message"))
                        else:
                            st.error("Failed to trigger email.")
            else:
                st.info("No unread resources. Good job!")

            st.divider()

            # Table 2: Shared Resources
            st.subheader("asd Shared Resources (Emailed)")
            if not shared_df.empty:
                # Select relevant columns including Matched Topic
                display_shared = shared_df[["title", "matched_topic", "type", "created_at", "url"]].copy()
                st.dataframe(display_shared, use_container_width=True)
            else:
                st.info("No emails sent yet.")
                
        else:
            st.info("No resources found in the database.")
            
    except Exception as e:
        st.error(f"Failed to load dashboard data: {e}")

elif page == "Upload Curriculum":
    st.header("Upload Curriculum")
    uploaded_file = st.file_uploader("Upload PDF or Text file", type=["pdf", "txt", "md"])
    
    if uploaded_file:
        if st.button("Process Curriculum"):
            with st.spinner("Processing curriculum... This may take a while as we generate embeddings."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/upload/curriculum", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Success! {data['message']}")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")

elif page == "Add Resource":
    st.header("Add Resource")
    url = st.text_input("Enter Resource URL (YouTube or Article)")
    
    if st.button("Add Resource"):
        if url:
            with st.spinner("Fetching and processing resource..."):
                try:
                    response = requests.post(f"{API_URL}/upload/resource", json={"url": url})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Success! {data['message']}")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")
        else:
            st.warning("Please enter a URL")
