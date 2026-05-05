import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from agents.monitor import analyze_channels
from agents.script_gen import generate_script, format_teleprompter
from agents.linkedin import generate_linkedin_posts
from agents.notifier import send_daily_digest

load_dotenv()

app = Flask(__name__)

DATA_DIR = 'data'
CACHE_FILE = f'{DATA_DIR}/video_cache.json'
SCRIPTS_FILE = f'{DATA_DIR}/scripts.json'
LINKEDIN_FILE = f'{DATA_DIR}/linkedin.json'

os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_channels():
    with open('config/channels.json') as f:
        return json.load(f)['channels']


@app.route('/')
def index():
    videos = load_json(CACHE_FILE, [])
    return render_template('index.html', videos=videos)


@app.route('/refresh', methods=['POST'])
def refresh():
    channels = load_channels()
    outliers = analyze_channels(channels)
    save_json(CACHE_FILE, outliers)
    return redirect(url_for('index'))


@app.route('/script/<video_id>')
def script_view(video_id):
    scripts = load_json(SCRIPTS_FILE, {})
    videos = load_json(CACHE_FILE, [])
    video = next((v for v in videos if v['id'] == video_id), None)
    script = scripts.get(video_id)
    teleprompter = format_teleprompter(script) if script else None
    return render_template('script.html', video=video, script=script, teleprompter=teleprompter)


@app.route('/generate_script/<video_id>', methods=['POST'])
def generate_script_route(video_id):
    videos = load_json(CACHE_FILE, [])
    video = next((v for v in videos if v['id'] == video_id), None)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    script = generate_script(video['title'], video['description'])
    scripts = load_json(SCRIPTS_FILE, {})
    scripts[video_id] = script
    save_json(SCRIPTS_FILE, scripts)
    return jsonify({'success': True, 'script': script})


@app.route('/linkedin/<video_id>')
def linkedin_view(video_id):
    posts_data = load_json(LINKEDIN_FILE, {})
    videos = load_json(CACHE_FILE, [])
    video = next((v for v in videos if v['id'] == video_id), None)
    posts = posts_data.get(video_id)
    return render_template('linkedin.html', video=video, posts=posts)


@app.route('/generate_linkedin/<video_id>', methods=['POST'])
def generate_linkedin_route(video_id):
    videos = load_json(CACHE_FILE, [])
    video = next((v for v in videos if v['id'] == video_id), None)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    scripts = load_json(SCRIPTS_FILE, {})
    content = scripts.get(video_id, video['description'])
    posts = generate_linkedin_posts(video['title'], content)
    posts_data = load_json(LINKEDIN_FILE, {})
    posts_data[video_id] = posts
    save_json(LINKEDIN_FILE, posts_data)
    return jsonify({'success': True, 'posts': posts})


@app.route('/send_digest', methods=['POST'])
def send_digest():
    videos = load_json(CACHE_FILE, [])
    send_daily_digest(videos)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
