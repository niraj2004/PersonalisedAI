import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

supabase: Client = create_client(url, key)

def check_table(table_name):
    print(f"Checking table '{table_name}'...")
    try:
        # Try to select 0 rows just to check existence/permission
        response = supabase.table(table_name).select("*").limit(1).execute()
        print(f"✅ Table '{table_name}' exists and is accessible.")
        return True
    except Exception as e:
        print(f"❌ Error accessing table '{table_name}': {e}")
        print("   (This usually means the table hasn't been created yet)")
        return False

print("--- Verifying Database Setup ---")
tables = ["curriculum_topics", "resources", "resource_chunks"]
all_exist = True

for table in tables:
    if not check_table(table):
        all_exist = False

if all_exist:
    print("\n🎉 Database verification PASSED! All tables are ready.")
else:
    print("\n⚠️ Database verification FAILED. Please run the schema.sql in your Supabase Dashboard.")
