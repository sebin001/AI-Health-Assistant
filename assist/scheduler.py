from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command


def run_medicine_reminders():
    call_command("send_medicine_reminders")


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_medicine_reminders,
        trigger="interval",
        minutes=1,
        id="medicine_reminder_job",
        replace_existing=True,
    )

    scheduler.start()

    print("Medicine reminder scheduler started.")