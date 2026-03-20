"""
Generate Thinking Audio Files
=============================

Creates short TTS audio clips for the "thinking" / "processing" states.
These play while the user waits for the AI response (during brain
classification, Tavily search, and LLM warm-up).

Run at startup (automatic) or manually:
    python -m app.generate_thinking_audio

Output: frontend/audio/starter_*.mp3

Uses edge-tts (same as main app TTS). No API key required.
"""

import asyncio
import sys
from pathlib import Path

# Project root is parent of app/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = PROJECT_ROOT / "frontend" / "audio"

# STARTER — Universal acknowledgments (min 3 words) for ANY query (greetings, questions, commands).
# Must not imply "searching" or "looking up" — e.g. "Hello" or "What's JavaScript?" would sound wrong.
STARTER_PHRASES = [
    ("starter_1", "One moment please."),
    ("starter_2", "Sure, one moment."),
    ("starter_3", "Got it, hold on."),
    ("starter_4", "On it right now."),
    ("starter_5", "Alright, give me a sec."),
    ("starter_6", "Right, one moment."),
    ("starter_7", "Okay, hold on."),
    ("starter_8", "One second please."),
    ("starter_9", "Give me a moment."),
    ("starter_10", "Just a moment please."),
]

PHRASES = STARTER_PHRASES

# Voice from config (en-GB-RyanNeural = JARVIS-style British male)
VOICE = "en-GB-RyanNeural"
RATE = "+15%"  # Slightly faster for status cues


async def generate_one(name: str, text: str) -> bool:
    """Generate one MP3 file. Returns True if created/updated."""
    try:
        import edge_tts
    except ImportError:
        return False
    path = AUDIO_DIR / f"{name}.mp3"
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(str(path))
        print(f"  [OK] {name}.mp3")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}.mp3: {e}")
        return False


async def main():
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("edge-tts not installed. Run: pip install edge-tts")
        return 1
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    # Remove any old followup files (no longer used)
    for f in AUDIO_DIR.glob("followup_*.mp3"):
        try:
            f.unlink()
            print(f"  [REMOVED] {f.name}")
        except OSError:
            pass
    print(f"Generating thinking audio in {AUDIO_DIR}...")
    success = 0
    for name, text in PHRASES:
        if await generate_one(name, text):
            success += 1
    print(f"Done: {success}/{len(PHRASES)} files.")
    return 0 if success == len(PHRASES) else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except KeyboardInterrupt:
        exit_code = 130
    sys.exit(exit_code)
