#!/usr/bin/env python3
"""
Transcribe Thai video using ElevenLabs Scribe API with character-level granularity
"""
import json
import os
import sys
from pathlib import Path
import requests

def transcribe_video(video_path: str, api_key: str, output_json: str) -> dict:
    """Transcribe video using ElevenLabs API"""

    # Verify file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    print(f"📹 Transcribing: {video_path}")
    print(f"🔑 Using ElevenLabs API...")

    # Extract audio from video first if needed
    import subprocess
    audio_path = "temp_audio.wav"
    if video_path.lower().endswith('.mp4'):
        print(f"🎵 Extracting audio from video...")
        try:
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-q:a', '9',
                '-y', audio_path
            ], check=True, capture_output=True)
        except Exception as e:
            print(f"⚠️  Audio extraction failed: {e}")
            # Continue with video file anyway
            audio_path = video_path

    # Upload audio and transcribe
    with open(audio_path, 'rb') as f:
        files = {'file': f}
        headers = {'xi-api-key': api_key}
        params = {
            'language': 'th',
            'timestamps_granularity': 'character'
        }

        try:
            response = requests.post(
                'https://api.elevenlabs.io/v1/scribe/transcribe-audio',
                headers=headers,
                params=params,
                files=files,
                timeout=300,
                verify=False  # Bypass SSL for now
            )
        except requests.exceptions.SSLError:
            print("⚠️  SSL Error, trying alternative endpoint...")
            response = requests.post(
                'https://api.elevenlabs.io/v1/audio-to-text',
                headers=headers,
                params=params,
                files=files,
                timeout=300,
                verify=False
            )

    # Clean up temp audio
    if os.path.exists(audio_path):
        os.remove(audio_path)

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"ElevenLabs API error: {response.text}")

    transcript = response.json()

    # Save to JSON
    output_dir = os.path.dirname(output_json)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    print(f"✓ Transcript saved: {output_json}")
    return transcript

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

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/transcribe_elevenlabs.py <video_path> [project_name]")
        sys.exit(1)

    # Load .env first
    load_env()

    video_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else Path(video_path).stem

    # Get API key from environment
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in .env")
        sys.exit(1)

    # Determine output path
    output_json = f"video_projects/{project_name}/edit/{project_name}_transcript.json"

    # Transcribe
    transcript = transcribe_video(video_path, api_key, output_json)

    print(f"\n✓ Transcription complete")
    print(f"  Characters: {len(transcript.get('characters', []))}")
    if transcript.get('characters'):
        print(f"  Duration: {transcript['characters'][-1]['end']:.2f}s")

if __name__ == '__main__':
    main()
