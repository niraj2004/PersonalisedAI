from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.processor import process_and_email_resource
import asyncio

scheduler = BackgroundScheduler()

def daily_job():
    print("Running daily job...")
    # We need to run the async function in a sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_and_email_resource())
    print("Daily job completed.")

def start_scheduler():
    # Run every day at 8:00 AM
    trigger = CronTrigger(hour=8, minute=0)
    scheduler.add_job(daily_job, trigger)
    scheduler.start()
    print("Scheduler started. Job scheduled for 8:00 AM daily.")
