import atexit
from datetime import datetime
import traceback
from database.settings_table import SettingsDatabaseManager
from logs import LogManager
log = LogManager.get_logger()
from globals import (CRON_JOB_PATH)
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None

def check_and_run_cron_jobs():
    cron_state_rows = SettingsDatabaseManager.get_cron_state()
    cron_state = cron_state_rows[0][0] if cron_state_rows else 'stopped'
    log.info(f"Cron state: {cron_state}")
    if cron_state == 'running' or cron_state == 'run_once':
        run_cron_jobs()
        if cron_state == 'run_once':
            SettingsDatabaseManager.update_cron_state('stopped')

def run_cron_jobs():
    try:
        result = subprocess.run(['python', CRON_JOB_PATH], check=True, text=True, capture_output=True)
        print(f"{result.stdout}")
    except Exception as e:
        log.error(f"An error occurred while running cron job: {e}")
        log.error(f"Traceback: {traceback.format_exc()}")

def run_scheduler():
    global scheduler
    try:
        if not scheduler:
            log.info("Initializing scheduler...")
            scheduler = BackgroundScheduler()
            check_and_run_cron_jobs()
            scheduler.add_job(func=check_and_run_cron_jobs, trigger="interval", hours=1)
            scheduler.start()
            atexit.register(lambda: scheduler.shutdown())
            log.info("Scheduler started.")
    except Exception as e:
        log.error("An error occurred while initializing the scheduler: %s", str(e))
        log.error("", traceback.format_exc())