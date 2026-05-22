#!/usr/bin/env python3
"""
Transcribe Thai video using ElevenLabs with better SSL handling
"""
import json
import os
import sys
import urllib3
from pathlib import Path

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    """Transcribe video using ElevenLabs API with urllib3"""

    print(f"[*] Transcribing: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Create HTTP connection with SSL verification disabled
    import urllib3.util.retry as retry_util
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    import requests

    session = requests.Session()

    # Configure retries
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    # Try multiple endpoints
    endpoints = [
        'https://api.elevenlabs.io/v1/scribe',
        'https://api.elevenlabs.io/v1/audio-to-text',
        'https://api.elevenlabs.io/v1/transcribe'
    ]

    for endpoint in endpoints:
        try:
            print(f"[*] Trying: {endpoint}")

            with open(video_path, 'rb') as f:
                files = {'file': f}
                headers = {'xi-api-key': api_key}
                params = {
                    'language': 'th',
                    'timestamps_granularity': 'character'
                }

                response = session.post(
                    endpoint,
                    headers=headers,
                    params=params,
                    files=files,
                    timeout=300,
                    verify=False
                )

            if response.status_code == 200:
                transcript = response.json()
                print(f"[OK] Transcription successful!")

                # Save to file
                output_dir = Path(output_json).parent
                output_dir.mkdir(parents=True, exist_ok=True)

                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(transcript, f, ensure_ascii=False, indent=2)

                print(f"[OK] Saved: {output_json}")
                return transcript
            else:
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")

        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
            continue

    raise Exception("All ElevenLabs endpoints failed")

def main():
    load_env()

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/transcribe_elevenlabs_v2.py <video_path> [project_name]")
        sys.exit(1)

    video_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else Path(video_path).stem

    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("[ERROR] ELEVENLABS_API_KEY not set")
        sys.exit(1)

    output_json = f"video_projects/{project_name}/edit/{project_name}_transcript.json"

    try:
        transcript = transcribe_video(video_path, api_key, output_json)
        print(f"\n[Summary]")
        if 'characters' in transcript:
            print(f"  Characters: {len(transcript['characters'])}")
            if transcript['characters']:
                print(f"  Duration: {transcript['characters'][-1].get('end', 0):.2f}s")
    except Exception as e:
        print(f"[FAILED] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
