import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANGLES = [
    "Contrarian take — challenge a belief most people in your niche hold",
    "Behind the scenes — what most people skip or don't know about this topic",
    "Numbered list — 3-5 specific things you learned or noticed",
    "Story format — a personal experience that led to this insight",
    "Question hook — open with a question that creates genuine curiosity",
    "Data or results — specific numbers, timelines, or outcomes from applying this",
]


def load_brand_blueprint():
    try:
        with open('brand_blueprint.md') as f:
            return f.read()
    except FileNotFoundError:
        return "Journaling channel for business owners and entrepreneurs aged 30-50."


def generate_linkedin_posts(video_title, script_excerpt):
    brand = load_brand_blueprint()
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    angles_text = '\n'.join(f"{i + 1}. {a}" for i, a in enumerate(ANGLES))

    message = client.messages.create(
        model='claude-opus-4-7',
        max_tokens=3000,
        system=[
            {
                'type': 'text',
                'text': f"You write LinkedIn posts for a creator. Match their voice exactly.\n\n{brand}",
                'cache_control': {'type': 'ephemeral'},
            }
        ],
        messages=[
            {
                'role': 'user',
                'content': f"""Generate 6 LinkedIn posts from this YouTube video. Each post uses a different angle.

VIDEO TITLE: {video_title}

CONTENT:
{script_excerpt[:2000]}

ANGLES (one post per angle, in order):
{angles_text}

RULES:
- No em dashes (—)
- No emoji bullet lists
- No phrases: "game-changer", "dive in", "leverage", "unleash", "in today's world", "it's time to"
- Short sentences. Direct. Real voice.
- Max 130 words per post
- End each post with one clear call to action (watch the video, comment, or share)
- Audience: business owners and entrepreneurs aged 30-50

Format as POST 1 through POST 6 with a blank line between each.""",
            }
        ],
    )
    return message.content[0].text
