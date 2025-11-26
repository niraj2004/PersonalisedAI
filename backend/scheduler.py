from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.processor import process_and_email_resource
from backend.db import supabase
import asyncio

scheduler = BackgroundScheduler()
JOB_ID = "daily_email_job"

def daily_job():
    print("Running daily job...")
    # We need to run the async function in a sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_and_email_resource())
    print("Daily job completed.")

def get_scheduled_time():
    try:
        res = supabase.table("settings").select("value").eq("key", "daily_email_time").single().execute()
        if res.data:
            time_str = res.data["value"]
            hour, minute = map(int, time_str.split(":"))
            return hour, minute
    except Exception as e:
        print(f"Error fetching schedule time: {e}")
    
    return 8, 0 # Default

def start_scheduler():
    hour, minute = get_scheduled_time()
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(daily_job, trigger, id=JOB_ID, replace_existing=True)
    scheduler.start()
    print(f"Scheduler started. Job scheduled for {hour:02d}:{minute:02d} daily.")

def reschedule_job(hour: int, minute: int):
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.reschedule_job(JOB_ID, trigger=trigger)
    print(f"Job rescheduled to {hour:02d}:{minute:02d}")

