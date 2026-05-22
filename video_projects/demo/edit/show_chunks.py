import json, sys
sys.stdout.reconfigure(encoding="utf-8")
from pythainlp import word_tokenize

EDIT_DIR  = "D:/demo/Claude-Thai-Video-Studio/video_projects/demo/edit"
GAP_BREAK = 0.25
MAX_CHARS = 18
LAST_CAP  = 0.28

edl      = json.load(open(f"{EDIT_DIR}/edl.json", encoding="utf-8-sig"))
segments = json.load(open(f"{EDIT_DIR}/transcript.json", encoding="utf-8-sig"))

def reconstruct_words(segs):
    out = []
    for seg in segs:
        if not seg.get("words"): continue
        chars = [{"text": w["word"], "start": w["start"], "end": w["end"]} for w in seg["words"]]
        out.append({"text": seg["text"].strip(), "start": seg["start"], "end": seg["end"], "chars": chars})
    return out

def map_to_output(phrase_words, edl_segs):
    out, offset = [], 0.0
    for seg in edl_segs:
        s, e = seg["start"], seg["end"]
        seg_dur = e - s
        for pw in phrase_words:
            if pw["start"] >= s and pw["start"] < e:
                ms = round((pw["start"]-s)+offset, 4)
                me = round(min((pw["end"]-s)+offset, offset+seg_dur), 4)
                mapped_chars = []
                for ch in pw["chars"]:
                    if ch["start"] >= s and ch["start"] < e:
                        cs = round((ch["start"]-s)+offset, 4)
                        ce = round(min((ch["end"]-s)+offset, offset+seg_dur), 4)
                        mapped_chars.append({"text": ch["text"], "start": cs, "end": ce})
                out.append({"text": pw["text"], "start": ms, "end": me, "chars": mapped_chars})
        offset += seg_dur
    return out

def expand_to_thai_words(phrase_words):
    expanded = []
    for pw in phrase_words:
        tokens = [t for t in word_tokenize(pw["text"], keep_whitespace=False) if t.strip()]
        chars, char_idx = pw["chars"], 0
        for tok in tokens:
            matched, remaining = [], tok
            while remaining and char_idx < len(chars):
                ch = chars[char_idx]; matched.append(ch); char_idx += 1
                remaining = remaining[len(ch["text"]):]
                if not remaining: break
            if not matched: continue
            last = matched[-1]; dur = last["end"]-last["start"]
            t_end = (last["start"]+min(dur, LAST_CAP)) if dur > 0.25 else last["end"]
            expanded.append({"text": tok, "start": matched[0]["start"], "end": t_end})
    return expanded

def build_chunks(words):
    merged = []
    for w in words:
        if w["text"] == "ๆ" and merged:
            p = merged[-1]; merged[-1] = {"text": p["text"]+"ๆ", "start": p["start"], "end": w["end"]}
        else:
            merged.append(w)
    chunks, cur = [], []
    for w in merged:
        if not cur: cur.append(w)
        else:
            gap = w["start"]-cur[-1]["end"]
            total = sum(len(x["text"]) for x in cur)+len(w["text"])
            if gap >= GAP_BREAK or total > MAX_CHARS: chunks.append(cur); cur = [w]
            else: cur.append(w)
    if cur: chunks.append(cur)
    return chunks

phrase_words = reconstruct_words(segments)
mapped = map_to_output(phrase_words, edl["segments"])
words = expand_to_thai_words(mapped)
chunks = build_chunks(words)

for i, chunk in enumerate(chunks):
    text = "".join(w["text"] for w in chunk)
    t0, t1 = chunk[0]["start"], chunk[-1]["end"]
    print(f"{i+1:2d}. [{t0:.2f}-{t1:.2f}] {text}")
