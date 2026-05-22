#!/usr/bin/env python3
"""
Transcribe Thai video using OpenAI Whisper API
"""
import json
import os
import sys
from pathlib import Path

def load_env():
    """Load .env file"""
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def transcribe_video(video_path: str, api_key: str, output_json: str) -> dict:
    """Transcribe video using OpenAI Whisper API"""

    print(f"[*] Transcribing with OpenAI Whisper...")
    print(f"    File: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        from openai import OpenAI
    except ImportError:
        print("[ERROR] openai library not installed")
        print("[FIX] Run: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Open and transcribe video file
    with open(video_path, 'rb') as audio_file:
        print("[*] Uploading to OpenAI Whisper...")

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="th",
            response_format="verbose_json"
        )

    print(f"[OK] Transcription complete!")

    # Convert to our format
    result = {
        "text": transcript.text,
        "duration": transcript.duration if hasattr(transcript, 'duration') else 0,
        "segments": []
    }

    # Extract segments if available
    if hasattr(transcript, 'segments'):
        for segment in transcript.segments:
            result['segments'].append({
                "id": segment.get('id', 0),
                "start": segment.get('start', 0),
                "end": segment.get('end', 0),
                "text": segment.get('text', ''),
                "words": segment.get('words', [])
            })

    # Save to file
    output_dir = Path(output_json).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved: {output_json}")
    return result

def main():
    load_env()

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/transcribe_whisper.py <video_path> [project_name]")
        sys.exit(1)

    video_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else Path(video_path).stem

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in .env")
        print("[FIX] Add to .env: OPENAI_API_KEY=sk_...")
        sys.exit(1)

    output_json = f"video_projects/{project_name}/edit/{project_name}_transcript.json"

    try:
        transcript = transcribe_video(video_path, api_key, output_json)

        print(f"\n[Summary]")
        print(f"  Text: {transcript['text'][:100]}...")
        print(f"  Duration: {transcript['duration']:.2f}s" if transcript['duration'] > 0 else "  Duration: N/A")
        print(f"  Segments: {len(transcript['segments'])}")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
