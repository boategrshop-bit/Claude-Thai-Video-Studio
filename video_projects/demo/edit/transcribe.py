import json, sys
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "D:/demo/Claude-Thai-Video-Studio/video_projects/demo/edit/audio.wav",
    language="th",
    word_timestamps=True,
    beam_size=5,
)

out = []
for seg in segments:
    words = []
    if seg.words:
        for w in seg.words:
            words.append({"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3)})
    out.append({"start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text, "words": words})

with open("D:/demo/Claude-Thai-Video-Studio/video_projects/demo/edit/transcript.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"Done: {len(out)} segments, lang={info.language}, prob={info.language_probability:.2f}")
for s in out:
    print(f"[{s['start']:.2f}-{s['end']:.2f}] {s['text']}")
