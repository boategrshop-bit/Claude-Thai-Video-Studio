#!/usr/bin/env python3
"""
Analyze video for dead air and propose cuts using ffmpeg silence detection
"""
import json
import subprocess
import sys
import os
from pathlib import Path

# Force UTF-8 output
os.environ['PYTHONIOENCODING'] = 'utf-8'

def extract_and_analyze(video_path: str) -> dict:
    """Extract audio and detect silence using ffmpeg silencedetect filter"""

    print(f"[*] Analyzing: {video_path}")

    # Get video info first
    probe_cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1:nokey=1',
        video_path
    ]

    try:
        duration_output = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        total_duration = float(duration_output.stdout.strip())
        print(f"[Duration] Total: {total_duration:.2f}s")
    except Exception as e:
        print(f"[Error] Failed to get duration: {e}")
        total_duration = 0

    # Detect silence segments using ffmpeg
    # silencedetect: d=0.4 means 0.4s of silence, n=-20dB means threshold
    silence_cmd = [
        'ffmpeg', '-i', video_path,
        '-af', 'silencedetect=d=0.4:n=-20dB',
        '-f', 'null', '-'
    ]

    try:
        result = subprocess.run(silence_cmd, capture_output=True, text=True)
        stderr = result.stderr

        # Parse silence segments - pair start with end
        silence_ranges = []
        lines = stderr.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if 'silence_start:' in line:
                try:
                    start_time = float(line.split('silence_start: ')[1].split()[0])
                    # Next line should be silence_end
                    if i + 1 < len(lines) and 'silence_end:' in lines[i + 1]:
                        end_line = lines[i + 1]
                        end_time = float(end_line.split('silence_end: ')[1].split()[0])
                        duration = float(end_line.split('|')[1].split(':')[1].strip())
                        silence_ranges.append({
                            'start': start_time,
                            'end': end_time,
                            'duration': duration
                        })
                        print(f"  Silence: {start_time:.3f}s - {end_time:.3f}s ({duration:.3f}s)")
                        i += 2
                    else:
                        i += 1
                except Exception as e:
                    i += 1
            else:
                i += 1

        return {
            'duration': total_duration,
            'silences': silence_ranges,
            'stderr': stderr[-500:]  # Last 500 chars of stderr for reference
        }

    except Exception as e:
        print(f"[Error] Silence detection failed: {e}")
        return {'duration': total_duration, 'silences': [], 'error': str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/analyze_video.py <video_path> [project_name]")
        sys.exit(1)

    video_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else Path(video_path).stem

    analysis = extract_and_analyze(video_path)
    analysis['source'] = video_path

    # Save to file
    output_json = f"video_projects/{project_name}/edit/silence_analysis.json"
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved: {output_json}")

if __name__ == '__main__':
    main()
