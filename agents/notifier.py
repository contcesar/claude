import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_daily_digest(outliers):
    webhook = os.getenv('SLACK_WEBHOOK_URL')

    if not outliers:
        requests.post(webhook, json={'text': 'Daily scan complete. No outlier videos found today.'})
        return

    blocks = [
        {
            'type': 'header',
            'text': {'type': 'plain_text', 'text': 'Daily Outlier Report'},
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'Found *{len(outliers)} outlier video{"s" if len(outliers) != 1 else ""}* worth adapting today.',
            },
        },
        {'type': 'divider'},
    ]

    for i, video in enumerate(outliers[:5]):
        blocks.append({
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': (
                    f'*{i + 1}. {video["title"]}*\n'
                    f'Channel: {video["channel_title"]} | '
                    f'Views: {video["views"]:,} | '
                    f'Score: *{video["outlier_score"]}x* avg\n'
                    f'<https://youtube.com/watch?v={video["id"]}|Watch on YouTube>'
                ),
            },
        })
        blocks.append({'type': 'divider'})

    blocks.append({
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': '<http://localhost:5000|Open Content Studio>',
        },
    })

    resp = requests.post(webhook, json={'blocks': blocks})
    return resp.status_code == 200


def send_message(text):
    webhook = os.getenv('SLACK_WEBHOOK_URL')
    resp = requests.post(webhook, json={'text': text})
    return resp.status_code == 200
