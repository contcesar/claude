import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

HOOK_FRAMEWORK = """Seven-step hook framework — use this exact structure for the intro:
1. Pattern interruption: grab attention immediately with an unexpected statement or bold claim
2. Mirror the viewer: speak directly to who they are and their current situation
3. Reveal the opportunity: tell them what they're about to learn or gain
4. Expose the gap: create curiosity about what they don't know yet
5. Promise the transformation: what specifically changes for them if they keep watching
6. Authority: briefly establish why you're qualified to share this (1-2 sentences max)
7. Transition: smooth bridge into the body of the content"""


def load_brand_blueprint():
    try:
        with open('brand_blueprint.md') as f:
            return f.read()
    except FileNotFoundError:
        return "Journaling channel for business owners and entrepreneurs aged 30-50."


def generate_script(video_title, video_description):
    brand = load_brand_blueprint()
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    message = client.messages.create(
        model='claude-opus-4-7',
        max_tokens=4000,
        system=[
            {
                'type': 'text',
                'text': f"You are a YouTube script writer. Write in the creator's exact voice based on their brand blueprint.\n\n{brand}",
                'cache_control': {'type': 'ephemeral'},
            }
        ],
        messages=[
            {
                'role': 'user',
                'content': f"""Write an original YouTube script inspired by this competitor video. Do NOT copy it — take only the topic angle and format, then rewrite entirely in the creator's voice.

COMPETITOR VIDEO (for format reference only):
Title: {video_title}
Description: {video_description}

HOOK FRAMEWORK (follow all 7 steps for the intro):
{HOOK_FRAMEWORK}

SCRIPT STRUCTURE:
- HOOK (all 7 steps, ~2 minutes when spoken at normal pace)
- BODY (main content with clear section headers)
- CALL TO ACTION (subscribe, comment prompt, share)

RULES:
- Sound like a real person talking, not AI-generated content
- No em dashes. No filler phrases. Short sentences where possible.
- Use [PAUSE] where the creator should pause for emphasis
- Use [B-ROLL: description] to suggest relevant footage
- Be specific — use real examples, numbers, scenarios
- Label each section clearly: HOOK / BODY / CALL TO ACTION""",
            }
        ],
    )
    return message.content[0].text


def format_teleprompter(script):
    lines = script.split('\n')
    formatted = []
    for line in lines:
        line = line.strip()
        if not line:
            formatted.append('')
            continue
        if line.startswith('#') or (line.isupper() and len(line) < 40):
            formatted.append(f'\n--- {line} ---\n')
            continue
        words = line.split()
        chunks = [' '.join(words[i:i + 7]) for i in range(0, len(words), 7)]
        formatted.extend(chunks)
    return '\n'.join(formatted)
