import trafilatura
import sys

try:
    url = "https://www.example.com"
    print(f"Fetching {url}...")
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        print("Failed to download.")
        sys.exit(1)
        
    print("Running bare_extraction...")
    data = trafilatura.bare_extraction(downloaded)
    
    print(f"Type of data: {type(data)}")
    print(f"Dir of data: {dir(data)}")
    
    if isinstance(data, dict):
        print("It is a dict.")
        print(data.keys())
    else:
        print("It is NOT a dict.")
        
except Exception as e:
    print(f"Error: {e}")
