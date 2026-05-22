#!/usr/bin/env python3
"""
Generate EDL (Edit Decision List) from silence detection
Keeps all non-silence segments
"""
import json
import sys
from pathlib import Path

def generate_edl_from_silence(video_path: str, silence_data: dict, output_edl: str):
    """Generate EDL by extracting kept segments (inverse of silence)"""

    print("[*] Generating EDL from silence data...")

    # Silence data already has proper start/end pairs
    silences = silence_data['silences']

    print(f"[Info] Found {len(silences)} silence segments")

    # Generate kept segments (inverse of silence)
    kept_segments = []
    current_time = 0.0

    for silence in silences:
        if current_time < silence['start']:
            segment_duration = silence['start'] - current_time
            kept_segments.append({
                'start': current_time,
                'end': silence['start'],
                'duration': segment_duration
            })
            print(f"  Keep: {current_time:.3f}s - {silence['start']:.3f}s ({segment_duration:.3f}s)")
        current_time = silence['end']

    # Add final segment if any
    if current_time < silence_data['duration']:
        final_duration = silence_data['duration'] - current_time
        kept_segments.append({
            'start': current_time,
            'end': silence_data['duration'],
            'duration': final_duration
        })
        print(f"  Keep: {current_time:.3f}s - {silence_data['duration']:.3f}s ({final_duration:.3f}s)")

    # Create EDL structure
    edl = {
        'source': video_path,
        'segments': []
    }

    # Build segments for EDL
    for i, seg in enumerate(kept_segments):
        edl['segments'].append({
            'id': i,
            'source_path': video_path,
            'start': seg['start'],
            'end': seg['end'],
            'duration': seg['duration']
        })

    # Save EDL
    output_dir = Path(output_edl).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_edl, 'w', encoding='utf-8') as f:
        json.dump(edl, f, ensure_ascii=False, indent=2)

    print(f"[OK] EDL saved: {output_edl}")
    print(f"[Info] Kept {len(kept_segments)} segments")
    print(f"[Info] Total duration: {sum(s['duration'] for s in edl['segments']):.2f}s")

    return edl

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/generate_edl.py <silence_data.json> <output_edl.json>")
        sys.exit(1)

    silence_json = sys.argv[1]
    output_edl = sys.argv[2]

    # Load silence data
    with open(silence_json, 'r', encoding='utf-8') as f:
        silence_data = json.load(f)

    # Generate EDL
    edl = generate_edl_from_silence(silence_data['source'] if 'source' in silence_data else 'raw_media/demo.mp4',
                                     silence_data, output_edl)

if __name__ == '__main__':
    main()
