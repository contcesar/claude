import json
import os
import schedule
import time
from agents.monitor import analyze_channels
from agents.notifier import send_daily_digest

DATA_DIR = 'data'
CACHE_FILE = f'{DATA_DIR}/video_cache.json'


def load_channels():
    with open('config/channels.json') as f:
        return json.load(f)['channels']


def run_daily():
    print('Running daily outlier scan...')
    channels = load_channels()
    outliers = analyze_channels(channels)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(outliers, f, indent=2)

    send_daily_digest(outliers)
    print(f'Done. Found {len(outliers)} outlier video(s).')


# Run at 8:00am daily
schedule.every().day.at('08:00').do(run_daily)

if __name__ == '__main__':
    print('Scheduler started. Running initial scan now...')
    run_daily()
    print('Waiting for next scheduled run at 08:00 daily. Ctrl+C to stop.')
    while True:
        schedule.run_pending()
        time.sleep(60)
