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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unread Resources", "0")
    with col2:
        st.metric("Topics Covered", "0")
    with col3:
        st.metric("Emails Sent", "0")

    st.divider()
    
    st.subheader("Processed Resources")
    try:
        resources = requests.get(f"{API_URL}/resources").json()
        if resources:
            for res in resources:
                with st.expander(f"{res['title']} ({res['type']})"):
                    st.write(f"**URL:** {res['url']}")
                    st.write(f"**Added:** {res['created_at']}")
                    if st.button(f"Trigger Email for this Resource", key=res['id']):
                        with st.spinner("Generating Email..."):
                            trigger_res = requests.post(f"{API_URL}/trigger-email", params={"resource_id": res['id']})
                            if trigger_res.status_code == 200:
                                data = trigger_res.json()
                                if data.get("status") == "success":
                                    st.success("Email Generated & Sent!")
                                    st.markdown(f"### {data['email']['subject']}")
                                    st.markdown(data['email']['body'])
                                else:
                                    st.info(data.get("message"))
                            else:
                                st.error("Failed to trigger email.")
        else:
            st.info("No resources added yet.")
    except Exception as e:
        st.error(f"Failed to fetch resources: {e}")

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
