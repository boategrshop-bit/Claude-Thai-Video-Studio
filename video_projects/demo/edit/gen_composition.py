"""
Generate hyperframes caption-highlight index.html for demo.mp4
Source: Whisper char-level tokens → pythainlp words → output timeline mapping
"""
import json, re
from pythainlp import word_tokenize

EDIT_DIR  = r"D:\demo\Claude-Thai-Video-Studio\video_projects\demo\edit"
COMP_DIR  = rf"{EDIT_DIR}\animations\slot_captions"
LAST_CAP  = 0.28
GAP_BREAK = 0.25
MAX_CHARS = 22

# ---------- 1. Load data ----------
edl      = json.load(open(f"{EDIT_DIR}/edl.json", encoding="utf-8-sig"))
segments = json.load(open(f"{EDIT_DIR}/transcript.json", encoding="utf-8-sig"))
edl_segs = edl["segments"]

# Ending phrase — hardcoded from targeted Whisper transcription of [89.21-91.47]
ENDING_SEG = {
    "text": "ไปเรียนรู้พร้อมกันนะครับ กับคอร์สนี้ครับ",
    "start": 89.21, "end": 91.47,
    "chars": [
        {"text": "ไป", "start": 89.21, "end": 89.35},
        {"text": "เร", "start": 89.35, "end": 89.45},
        {"text": "ี",  "start": 89.45, "end": 89.45},
        {"text": "ย",  "start": 89.45, "end": 89.51},
        {"text": "น",  "start": 89.51, "end": 89.55},
        {"text": "ร",  "start": 89.55, "end": 89.57},
        {"text": "ู้", "start": 89.57, "end": 89.73},
        {"text": "พ",  "start": 89.73, "end": 89.77},
        {"text": "ร",  "start": 89.77, "end": 89.89},
        {"text": "้",  "start": 89.89, "end": 89.91},
        {"text": "อ",  "start": 89.91, "end": 89.95},
        {"text": "ม",  "start": 89.95, "end": 89.97},
        {"text": "ก",  "start": 89.97, "end": 90.01},
        {"text": "ั",  "start": 90.01, "end": 90.09},
        {"text": "น",  "start": 90.09, "end": 90.15},
        {"text": "นะ", "start": 90.15, "end": 90.21},
        {"text": "คร", "start": 90.21, "end": 90.33},
        {"text": "ั",  "start": 90.33, "end": 90.43},
        {"text": "บ",  "start": 90.43, "end": 90.49},
        {"text": "ก",  "start": 90.49, "end": 90.61},  # " ก" stripped
        {"text": "ั",  "start": 90.61, "end": 90.85},
        {"text": "บ",  "start": 90.85, "end": 90.91},
        {"text": "ค",  "start": 90.91, "end": 91.01},
        {"text": "อ",  "start": 91.01, "end": 91.11},
        {"text": "ร",  "start": 91.11, "end": 91.11},
        {"text": "์",  "start": 91.11, "end": 91.19},
        {"text": "ส",  "start": 91.19, "end": 91.19},
        {"text": "น",  "start": 91.19, "end": 91.19},
        {"text": "ี้", "start": 91.19, "end": 91.27},
        {"text": "คร", "start": 91.27, "end": 91.39},
        {"text": "ั",  "start": 91.39, "end": 91.47},
        {"text": "บ",  "start": 91.47, "end": 91.47},
    ]
}

# ---------- 2. reconstruct_words ----------
def reconstruct_words(segments):
    out = []
    for seg in segments:
        if not seg.get("words"):
            continue
        chars = [{"text": w["word"].strip(), "start": w["start"], "end": w["end"]}
                 for w in seg["words"] if w["word"].strip()]
        out.append({"text": seg["text"].strip(), "start": seg["start"], "end": seg["end"], "chars": chars})
    return out

phrase_words = reconstruct_words(segments)
# Remove any original transcript segments that overlap with ENDING_SEG (e.g. "นี้ครับ" at 91.20)
phrase_words = [pw for pw in phrase_words if not (pw["start"] >= 89.21 and pw["start"] < 91.47)]
# Append hardcoded ending
phrase_words.append(ENDING_SEG)

# ---------- 3. map_to_output (start-based, Bug 3 fix) ----------
def map_to_output(phrase_words, edl_segs):
    out, offset = [], 0.0
    for seg in edl_segs:
        s, e = seg["start"], seg["end"]
        seg_dur = e - s
        for pw in phrase_words:
            if pw["start"] >= s and pw["start"] < e:
                ms = round((pw["start"] - s) + offset, 4)
                me = round(min((pw["end"] - s) + offset, offset + seg_dur), 4)
                mapped_chars = []
                for ch in pw["chars"]:
                    if ch["start"] >= s and ch["start"] < e:
                        cs = round((ch["start"] - s) + offset, 4)
                        ce = round(min((ch["end"] - s) + offset, offset + seg_dur), 4)
                        mapped_chars.append({"text": ch["text"], "start": cs, "end": ce})
                out.append({"text": pw["text"], "start": ms, "end": me, "chars": mapped_chars})
        offset += seg_dur
    return out

mapped = map_to_output(phrase_words, edl_segs)
mapped.sort(key=lambda pw: pw["start"])  # ensure chronological order

# ---------- 4. expand_to_thai_words (char-anchored, Bug 4 fix) ----------
def expand_to_thai_words(phrase_words):
    expanded = []
    for pw in phrase_words:
        tokens = [t for t in word_tokenize(pw["text"], keep_whitespace=False) if t.strip()]
        chars, char_idx = pw["chars"], 0
        for tok in tokens:
            matched, remaining = [], tok
            while remaining and char_idx < len(chars):
                ch = chars[char_idx]
                matched.append(ch)
                char_idx += 1
                remaining = remaining[len(ch["text"]):]
                if not remaining:
                    break
            if not matched:
                continue
            last = matched[-1]
            dur = last["end"] - last["start"]
            t_end = (last["start"] + min(dur, LAST_CAP)) if dur > 0.25 else last["end"]
            expanded.append({"text": tok, "start": matched[0]["start"], "end": t_end})
    return expanded

# ---------- 5. apply_word_corrections ----------
def apply_word_corrections(words):
    """Text overrides: brand name fixes + Dead air + ending คอร์ส→Claude kept."""
    result = []
    i = 0
    while i < len(words):
        w = words[i]

        # Merge คอร์ + สนะ → Claude (group 18, ~20.86s)
        if w["text"] == "คอร์" and i+1 < len(words) and words[i+1]["text"] == "สนะ":
            result.append({"text": "Claude", "start": w["start"], "end": words[i+1]["end"]})
            i += 2; continue

        # เล็ก + แอร์  or  เล็กแอร์  →  Dead air
        if w["text"] == "เล็กแอร์":
            mid = round((w["start"] + w["end"]) / 2, 3)
            result.append({"text": "Dead", "start": w["start"], "end": mid})
            result.append({"text": "air",  "start": mid,        "end": w["end"]})
            i += 1; continue
        if w["text"] == "เล็ก" and i+1 < len(words) and words[i+1]["text"] == "แอร์":
            result.append({"text": "Dead", "start": w["start"],          "end": w["end"]})
            result.append({"text": "air",  "start": words[i+1]["start"], "end": words[i+1]["end"]})
            i += 2; continue

        # คอร์ส → Claude only at the three specific time ranges where speaker says "Claude"
        if w["text"] == "คอร์ส" and (
            (1.40 <= w["start"] <= 1.90) or   # group 2
            (8.70 <= w["start"] <= 9.20) or   # group 8
            (22.60 <= w["start"] <= 23.10)    # group 20
        ):
            result.append({"text": "Claude", "start": w["start"], "end": w["end"]})
            i += 1; continue

        result.append(w)
        i += 1
    return result

# ---------- 6. build_chunks (ๆ merge + Bug 1 fix + seg boundary) ----------
def build_chunks(words, seg_boundaries=None):
    merged = []
    for w in words:
        if w["text"] == "ๆ" and merged:
            p = merged[-1]
            merged[-1] = {"text": p["text"] + "ๆ", "start": p["start"], "end": w["end"]}
        else:
            merged.append(w)

    chunks, cur = [], []
    for w in merged:
        if not cur:
            cur.append(w)
        else:
            gap      = w["start"] - cur[-1]["end"]
            total_ch = sum(len(x["text"]) for x in cur) + len(w["text"])
            # Force split at EDL segment boundaries (no cross-cut chunks)
            crosses = seg_boundaries and any(
                cur[-1]["end"] <= b <= w["start"] or
                cur[0]["start"] < b <= w["start"]
                for b in seg_boundaries
            )
            if gap >= GAP_BREAK or total_ch > MAX_CHARS or crosses:
                chunks.append(cur); cur = [w]
            else:
                cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks

# ---------- 7. fix_chunks — group-level text overrides by output time ----------
def _set_words(chunk, texts):
    """Replace displayed texts; extend or trim chunk to match text list."""
    for j, t in enumerate(texts):
        if j < len(chunk):
            chunk[j]["text"] = t
        else:
            last = chunk[-1]
            chunk.append({"text": t, "start": last["end"], "end": min(last["end"] + 0.12, last["end"] + 0.12)})
    del chunk[len(texts):]

def fix_chunks(chunks):
    for ch in chunks:
        if not ch:
            continue
        t0 = ch[0]["start"]

        # Group at output ~35.5-37.2 (Dead air หรือในช่วง) — already correct from corrections

        # Group at output ~37.2-38.5 → "ที่เราพูดหรือมี"
        if 37.0 <= t0 <= 38.0:
            _set_words(ch, ["ที่เรา", "พูด", "หรือ", "มี"])

        # Group at output ~38.0-39.2 → "เทคที่ไม่ดีนะครับเช่น"
        elif 38.0 <= t0 <= 39.0:
            _set_words(ch, ["เทค", "ที่", "ไม่ดี", "นะครับ", "เช่น"])

        # Group at output ~40.0-41.1 (bad-take ending) → "พูดไม่รู้เรื่องอ่ะ"
        elif 39.8 <= t0 <= 41.2 and any("พูด" in w["text"] or "เรื่อง" in w["text"] for w in ch):
            _set_words(ch, ["พูด", "ไม่รู้", "เรื่อง", "อ่ะ"])

    # Remove lone "อ่ะ" chunks that are duplicates after group-30 override
    chunks = [ch for ch in chunks if not (len(ch) == 1 and ch[0]["text"] == "อ่ะ" and ch[0]["start"] > 40.0)]
    return chunks

# Compute output segment boundary times (force chunk splits at edit cuts)
seg_boundaries = []
_off = 0.0
for seg in edl_segs:
    _off += seg["end"] - seg["start"]
    seg_boundaries.append(round(_off, 4))

# ---------- Run pipeline ----------
words   = apply_word_corrections(expand_to_thai_words(mapped))
chunks  = fix_chunks(build_chunks(words, seg_boundaries))

all_words  = [w for chunk in chunks for w in chunk]
raw_groups = []
idx = 0
for chunk in chunks:
    raw_groups.append([idx, idx + len(chunk) - 1])
    idx += len(chunk)

total_dur = round(sum(s["end"] - s["start"] for s in edl_segs), 2)
print(f"Words: {len(all_words)}, Chunks: {len(chunks)}, Total dur: {total_dur}s")

# ---------- 8. Write index.html ----------
def js_words(words):
    items = ",\n  ".join(
        f'{{text:{json.dumps(w["text"], ensure_ascii=False)},start:{w["start"]},end:{w["end"]}}}'
        for w in words
    )
    return f"[\n  {items}\n]"

def js_raw_groups(groups):
    items = ",\n  ".join(f"[{g[0]},{g[1]}]" for g in groups)
    return f"[\n  {items}\n]"

tpl_path = f"{COMP_DIR}/index.html"
html = open(tpl_path, encoding="utf-8").read()

html = re.sub(r'var WORDS\s*=\s*\[.*?\];',       f'var WORDS = {js_words(all_words)};',       html, flags=re.DOTALL)
html = re.sub(r'var RAW_GROUPS\s*=\s*\[.*?\];',   f'var RAW_GROUPS = {js_raw_groups(raw_groups)};', html, flags=re.DOTALL)
html = re.sub(r'data-duration="[^"]*"',            f'data-duration="{total_dur}"',               html)
# No gap between Thai words
html = html.replace("gap: 6px;", "gap: 0;")

with open(tpl_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Written: {tpl_path}")
print("\nAll chunks:")
for i, chunk in enumerate(chunks):
    text = "".join(w["text"] for w in chunk)
    print(f"{i+1:2d}. [{chunk[0]['start']:.2f}-{chunk[-1]['end']:.2f}] {text}")
