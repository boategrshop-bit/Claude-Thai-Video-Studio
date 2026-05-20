# Caption Philosophy

ระบบซับไตเติ้ลแบบ karaoke per-word สำหรับวิดีโอ TikTok ภาษาไทย

---

## Component

ใช้ **`caption-highlight`** (แนะนำ) หรือ `caption-gradient-fill`

```bash
npx.cmd hyperframes add caption-highlight
```

`caption-highlight` ดีกว่าสำหรับ per-word emphasis — red pill sweep เข้าทีละคำ

---

## Canvas Spec

| Property | Value |
|----------|-------|
| ขนาด | 1080 × 1920 px |
| ตำแหน่ง subtitle | `bottom: 360px` |
| font-size | `64px` |
| maxWidth | `984px` (1080 − 2×48px padding) |
| data-fps | `"24"` |
| Font | `"Noto Sans Thai", sans-serif` weight `800` |

**ห้ามใช้ Leelawadee UI** — เป็น Windows GDI font ที่ headless Chromium ไม่มี

---

## Thai Adaptations (บังคับ)

```javascript
// ลบออก — ภาษาไทยไม่มี case
// text-transform: uppercase
// word.toUpperCase()

// fitFontSize string
"800 46px 'Noto Sans Thai', sans-serif"

// composition-id
data-composition-id="caption-highlight"
window.__timelines["caption-highlight"] = tl
```

---

## Thai Word Timing (pythainlp)

ElevenLabs Scribe ให้ phrase-level timing สำหรับภาษาไทย ต้องแตก phrase → per-word
ด้วย proportional timing:

```python
from pythainlp import word_tokenize  # uv run --with pythainlp

def expand_to_thai_words(phrase_words):
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
            expanded.append(dict(text=tok, start=round(t_cur, 4), end=t_end))
            t_cur = t_end
    return expanded
```

> Proportional timing เป็น approximation (char count ≠ speech duration)
> Brand names/loanwords อาจถูกแยกโดย pythainlp — timing ยังถูกตาม proportion

---

## Chunking Rules

```python
GAP_BREAK = 0.03    # สำหรับ per-word karaoke (within-phrase gap ≈ 0)
MAX_CHARS = 14      # Thai chars ต่อ group (4–6 คำ)
```

> `GAP_BREAK = 0.4` สำหรับ phrase-level chunking
> `GAP_BREAK = 0.03` สำหรับ per-word karaoke (default ที่แนะนำ)

---

## ๆ Bug Fix (CRITICAL)

`build_chunks()` merge standalone `ๆ` เข้ากับคำก่อนหน้า **ก่อน** chunking → word count ลดลง
ถ้าส่ง original word list ใน `js_array()` index จะผิดทุก group หลังตำแหน่ง ๆ

**Fix:**
```python
# WRONG
words_js, groups_js = js_array(out, cks)

# CORRECT — flatten จาก chunks เท่านั้น
def js_array(chunks):
    all_words = [w for chunk in chunks for w in chunk]
    # ... build JS arrays from all_words and chunks

words_js, groups_js = js_array(cks)
```

---

## Data Format (caption-highlight)

```javascript
var WORDS = [{ text: "คำ", start: 0.0, end: 0.3 }, ...];
var RAW_GROUPS = [[0, 4], [5, 9], ...];  // index pairs เข้า WORDS
// GROUPS computed at runtime
```

---

## Render Process

```bash
# 1. Lint ก่อนเสมอ
npx.cmd hyperframes lint --verbose
# ต้องได้ 0 errors — ถ้ามี error แก้ก่อน render

# 2. Render
npx.cmd hyperframes render --format webm -o render.webm
```

---

## VP9 Alpha Bug (CRITICAL)

ffmpeg native `vp9` decoder **ไม่รองรับ** alpha channel จาก hyperframes WebM
output จะดูเหมือนพื้นหลังดำทับ base video ทั้งหมด

**Fix:** ต้องระบุ `-vcodec libvpx-vp9` บน WebM input เสมอ:

```bash
ffmpeg \
  -i base_preview.mp4 \
  -vcodec libvpx-vp9 -i render.webm \
  -filter_complex "[0:v][1:v]overlay=0:0[v]" \
  -map "[v]" -map "0:a" ...
```

**Diagnosis:** ถ้า output file เล็กผิดปกติ (~2.6 MB แทนที่จะเป็น ~38 MB สำหรับคลิป 87s)
แสดงว่า alpha decoding ล้มเหลว

---

## Word Emphasis Style

สไตล์ที่ user ต้องการ:
- Active word: **ใหญ่ขึ้น** (scale 1.1×), สีสว่าง/เหลือง
- Inactive words: สีหม่น/เทา
- Effect ต้องชัดเจน — gradient sweep เบาๆ ไม่พอ
- Timing แน่น — subtitle ขึ้น/ลงตามเสียงพูด

---

## Quality Check

หลัง composite ดู:
1. Subtitle ขึ้น/ลงตรงกับเสียง?
2. Word highlight ชัดไหม?
3. File size สมเหตุสมผล? (~30–50 MB สำหรับคลิป 1–2 นาที)
4. ไม่มีพื้นหลังดำ? (VP9 alpha bug)
