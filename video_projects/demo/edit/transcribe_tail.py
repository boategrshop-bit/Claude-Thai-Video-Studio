import json
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "D:/demo/Claude-Thai-Video-Studio/video_projects/demo/edit/tail_audio.wav",
    language="th",
    word_timestamps=True,
    beam_size=5,
)

OFFSET = 67.0  # seconds offset back to original timeline
for seg in segments:
    orig_start = seg.start + OFFSET
    orig_end   = seg.end   + OFFSET
    print(f"[{orig_start:.2f}-{orig_end:.2f}] {seg.text}")
