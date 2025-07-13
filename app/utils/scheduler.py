from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.reminder import send_appointment_reminders
from app.jobs.monthly_report import generate_monthly_reports

scheduler = BackgroundScheduler()

def start():
    scheduler.add_job(send_appointment_reminders, 'cron', hour=0, minute=0)  # Every day at 00:00
    scheduler.add_job(generate_monthly_reports, 'cron', day=1, hour=1)        # 1st of month at 01:00
    scheduler.start()
