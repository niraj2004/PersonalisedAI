import requests
import json

API_URL = "http://localhost:8000"

def test_trigger_email():
    print("Testing /trigger-email endpoint...")
    try:
        response = requests.post(f"{API_URL}/trigger-email")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Full Response: {json.dumps(data, indent=2)}")
            
            if data.get("status") == "success":
                print("\n✅ Success!")
                print(f"Matched Topic: {data['match']['topic']}")
                print(f"Similarity: {data['match']['similarity']:.4f}")
                print("\n--- Generated Email ---")
                print(f"Subject: {data['email']['subject']}")
                print("-" * 20)
                print(data['email']['body'][:500] + "...\n[truncated]")
                
                if "delivery" in data:
                    print(f"\n📧 Delivery Status: {data['delivery']}")
            else:
                print(f"ℹ️ API returned: {data.get('message')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_trigger_email()
