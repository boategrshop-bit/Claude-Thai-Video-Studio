#!/usr/bin/env python3
"""
Generate caption composition for hyperframes
Creates an HTML composition with Thai words grouped 4-5 per line
with red highlight animation synchronized to video
"""
import json
import os
from pathlib import Path

def create_caption_html(base_preview_path: str, project_name: str, output_dir: str):
    """Create HTML caption composition for hyperframes"""

    print(f"[*] Creating caption composition...")

    os.makedirs(output_dir, exist_ok=True)

    # Generate a sample caption sequence with red highlights
    # In real scenario, this would be generated from ElevenLabs transcript
    sample_captions = [
        {"start": 0.5, "end": 2.5, "text": "สวัสดีค่ะ", "words": [{"text": "สวัสดีค่ะ", "start": 0.5, "end": 2.5}]},
        {"start": 2.8, "end": 4.5, "text": "ยินดีต้อนรับ", "words": [{"text": "ยินดี", "start": 2.8, "end": 3.5}, {"text": "ต้อนรับ", "start": 3.5, "end": 4.5}]},
        {"start": 5.0, "end": 7.0, "text": "ขอบคุณที่มา", "words": [{"text": "ขอบคุณ", "start": 5.0, "end": 6.0}, {"text": "ที่มา", "start": 6.0, "end": 7.0}]},
        {"start": 7.5, "end": 9.5, "text": "วันนี้พบเจอกัน", "words": [
            {"text": "วันนี้", "start": 7.5, "end": 8.2},
            {"text": "พบเจอ", "start": 8.2, "end": 8.9},
            {"text": "กัน", "start": 8.9, "end": 9.5}
        ]},
    ]

    # Create HTML composition
    html_content = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thai Captions with Highlights</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: "Noto Sans Thai", sans-serif;
            overflow: hidden;
        }

        #canvas {
            width: 1080px;
            height: 1920px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            background: transparent;
        }

        .caption-area {
            width: 984px;
            margin-bottom: 360px;
            text-align: center;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }

        .word {
            font-size: 64px;
            font-weight: 800;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            line-height: 1.2;
            display: inline;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .word.highlight {
            color: #ff1744;
            text-shadow: 2px 2px 8px rgba(255, 23, 68, 0.8),
                         0 0 15px rgba(255, 23, 68, 0.6);
            animation: pulse 0.4s ease-in-out;
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
                text-shadow: 2px 2px 8px rgba(255, 23, 68, 0.8),
                           0 0 15px rgba(255, 23, 68, 0.6);
            }
            50% {
                transform: scale(1.05);
                text-shadow: 2px 2px 8px rgba(255, 23, 68, 1),
                           0 0 20px rgba(255, 23, 68, 1);
            }
            100% {
                transform: scale(1);
                text-shadow: 2px 2px 8px rgba(255, 23, 68, 0.8),
                           0 0 15px rgba(255, 23, 68, 0.6);
            }
        }
    </style>
</head>
<body>
    <div id="canvas">
        <div class="caption-area" id="captions"></div>
    </div>

    <script>
        // Sample captions with timing and word-level information
        const captions = ''' + json.dumps(sample_captions) + ''';

        // Build caption display
        const captionsDiv = document.getElementById('captions');
        const wordElements = [];

        captions.forEach((caption, idx) => {
            caption.words.forEach((word) => {
                const wordSpan = document.createElement('span');
                wordSpan.className = 'word';
                wordSpan.textContent = word.text + ' ';
                wordSpan.dataset.start = word.start;
                wordSpan.dataset.end = word.end;
                captionsDiv.appendChild(wordSpan);
                wordElements.push(wordSpan);
            });
        });

        // Animation timing (synchronized with video)
        const videoElement = document.querySelector('video') || {currentTime: 0};

        setInterval(() => {
            const currentTime = videoElement.currentTime || (Date.now() / 1000 % 100);

            wordElements.forEach(el => {
                const start = parseFloat(el.dataset.start);
                const end = parseFloat(el.dataset.end);

                if (currentTime >= start && currentTime < end) {
                    el.classList.add('highlight');
                } else {
                    el.classList.remove('highlight');
                }
            });
        }, 50);
    </script>
</body>
</html>
'''

    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[OK] Created: {index_path}")
    return index_path

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/create_captions.py <project_name> [base_preview.mp4]")
        sys.exit(1)

    project_name = sys.argv[1]
    base_preview = sys.argv[2] if len(sys.argv) > 2 else f"video_projects/{project_name}/edit/base_preview.mp4"

    output_dir = f"video_projects/{project_name}/edit/animations/slot_captions"
    create_caption_html(base_preview, project_name, output_dir)

if __name__ == '__main__':
    main()
