"""
gen_composition.py — Generate hyperframes caption-highlight index.html from transcript + edl.json
Usage: uv run --with pythainlp scripts/gen_composition.py <transcript.json> <edl.json> <output_dir>

Output: <output_dir>/index.html  (ready for `npx.cmd hyperframes render`)
"""
import json
import sys
from pathlib import Path

try:
    from pythainlp import word_tokenize
except ImportError:
    sys.exit("pythainlp not found. Run: uv run --with pythainlp scripts/gen_composition.py ...")


# ── Tuning ──────────────────────────────────────────────────────────────────
GAP_BREAK = 0.03    # seconds gap to split into new group (0.03 for per-word karaoke)
MAX_CHARS = 14      # max Thai chars per group
FPS = 24
# ────────────────────────────────────────────────────────────────────────────


def reconstruct_words(characters: list) -> list:
    words, current_chars, current_start = [], [], None
    for ch in characters:
        if ch["character"] == " ":
            if current_chars:
                words.append({
                    "text": "".join(c["character"] for c in current_chars),
                    "start": current_start,
                    "end": current_chars[-1]["end"],
                })
                current_chars, current_start = [], None
        else:
            if not current_chars:
                current_start = ch["start"]
            current_chars.append(ch)
    if current_chars:
        words.append({
            "text": "".join(c["character"] for c in current_chars),
            "start": current_start,
            "end": current_chars[-1]["end"],
        })
    return words


def map_to_output(words: list, segments: list) -> list:
    """Remap source timestamps → output timeline using EDL segments."""
    result = []
    offset = 0.0
    for seg in segments:
        seg_dur = seg["end"] - seg["start"]
        for w in words:
            if w["start"] >= seg["start"] and w["end"] <= seg["end"]:
                result.append({
                    "text": w["text"],
                    "start": round(w["start"] - seg["start"] + offset, 4),
                    "end": round(w["end"] - seg["start"] + offset, 4),
                })
        offset += seg_dur
    return result


def expand_to_thai_words(phrase_words: list) -> list:
    """Split phrase-level words into per-Thai-word timing (proportional)."""
    expanded = []
    for pw in phrase_words:
        tokens = [t for t in word_tokenize(pw["text"], keep_whitespace=False) if t.strip()]
        if not tokens:
            continue
        total_chars = sum(len(t) for t in tokens) or 1
        dur = pw["end"] - pw["start"]
        t_cur = pw["start"]
        for tok in tokens:
            frac = len(tok) / total_chars
            t_end = round(t_cur + frac * dur, 4)
            expanded.append({"text": tok, "start": round(t_cur, 4), "end": t_end})
            t_cur = t_end
    return expanded


def merge_mai_yamok(words: list) -> list:
    """Merge standalone ๆ into preceding word."""
    merged = []
    for w in words:
        if w["text"] == "ๆ" and merged:
            prev = merged[-1]
            merged[-1] = {
                "text": prev["text"] + "ๆ",
                "start": prev["start"],
                "end": w["end"],
            }
        else:
            merged.append(w)
    return merged


def build_chunks(words: list) -> list:
    """Group words into display chunks by gap and char limit."""
    chunks, current = [], []
    for w in words:
        if current:
            gap = w["start"] - current[-1]["end"]
            current_chars = sum(len(x["text"]) for x in current)
            if gap > GAP_BREAK or current_chars + len(w["text"]) > MAX_CHARS:
                chunks.append(current)
                current = []
        current.append(w)
    if current:
        chunks.append(current)
    return chunks


def js_array(chunks: list) -> tuple[str, str]:
    """Build WORDS and RAW_GROUPS JS arrays. Flatten from chunks — critical for ๆ index sync."""
    all_words = [w for chunk in chunks for w in chunk]

    words_items = ", ".join(
        f'{{text: "{w["text"]}", start: {w["start"]}, end: {w["end"]}}}'
        for w in all_words
    )
    words_js = f"var WORDS = [{words_items}];"

    idx = 0
    group_items = []
    for chunk in chunks:
        start_idx = idx
        end_idx = idx + len(chunk) - 1
        group_items.append(f"[{start_idx}, {end_idx}]")
        idx += len(chunk)
    groups_js = f"var RAW_GROUPS = [{', '.join(group_items)}];"

    return words_js, groups_js


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: transparent; }}
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@800&display=swap');
  body {{ font-family: 'Noto Sans Thai', sans-serif; font-weight: 800; }}
</style>
</head>
<body data-fps="{fps}" data-composition-id="caption-highlight">
<div id="caption-highlight-slot"
  style="position:absolute; bottom:360px; width:1080px; text-align:center; padding: 0 48px;">
</div>
<script>
{words_js}
{groups_js}
</script>
<script src="./caption-highlight.js"></script>
</body>
</html>
"""


def generate(transcript_path: Path, edl_path: Path, output_dir: Path):
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    edl = json.loads(edl_path.read_text(encoding="utf-8"))

    # Support both flat character list and nested {"characters": [...]}
    characters = transcript if isinstance(transcript, list) else transcript.get("characters", [])

    words = reconstruct_words(characters)
    words = map_to_output(words, edl["segments"])
    words = expand_to_thai_words(words)
    words = merge_mai_yamok(words)
    chunks = build_chunks(words)
    words_js, groups_js = js_array(chunks)

    output_dir.mkdir(parents=True, exist_ok=True)
    html = HTML_TEMPLATE.format(fps=FPS, words_js=words_js, groups_js=groups_js)
    (output_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Generated {len(words)} words → {len(chunks)} groups")
    print(f"Output: {output_dir / 'index.html'}")
    print(f"\nNext: cd {output_dir} && npx.cmd hyperframes lint --verbose")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("Usage: uv run --with pythainlp scripts/gen_composition.py <transcript.json> <edl.json> <output_dir>")
    generate(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
