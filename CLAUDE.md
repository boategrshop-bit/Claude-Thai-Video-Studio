# Claude Thai Video Editing Studio

Workspace สำหรับตัดต่อวิดีโอภาษาไทย รูปแบบ TikTok แนวตั้ง (1080×1920)
เนื้อหา: สัมภาษณ์ testimonial (host + นักเรียน/ลูกค้า)

**อ่าน philosophy docs ทั้งสามก่อนเริ่มทุกครั้ง:**
- `THAI_CONTENT_PHILOSOPHY.md` — สไตล์คอนเทนต์, การตัด, การจัดการ transcript ภาษาไทย
- `CAPTION_PHILOSOPHY.md` — ระบบซับไตเติ้ล hyperframes, Thai adaptations, bugs ที่รู้แล้ว
- `AUDIO_PHILOSOPHY.md` — loudnorm, BGM mixing, audio pipeline

---

## Prerequisites (ตรวจสอบทุกครั้งก่อนเริ่ม session)

```powershell
# PATH setup (PowerShell)
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

- `.env` มี `ELEVENLABS_API_KEY=...`
- Node.js 22+ (`node --version`)
- ffmpeg build ที่มี libvpx-vp9 (`ffmpeg -encoders | findstr vpx`)
- uv สำหรับ Python (`uv --version`)

---

## Standard Pipeline

### Step 1 — Transcribe

ใช้ ElevenLabs Scribe via `video-use` skill

```
timestamps_granularity: "character"
```

> ภาษาไทยได้ character-level tokens เสมอ ไม่ว่าจะตั้ง `word` หรือ `character`
> ต้อง call `reconstruct_words()` ก่อนทำ timing ทุกครั้ง

บันทึก transcript ที่: `video_projects/<name>/edit/<name>_transcript.json`

---

### Step 2 — Propose Cuts

วิเคราะห์และเสนอ cut plan เป็นภาษาธรรมดา:
- Dead air ≥ 0.4s
- Verbal stutters (คำซ้ำ/วลีซ้ำ)

**รอ user confirm ก่อนเขียน EDL ทุกครั้ง — ห้ามข้ามขั้นตอนนี้**

---

### Step 3 — Build EDL & Base Preview

เขียน `video_projects/<name>/edit/edl.json` แล้ว render base preview:
- CRF 22, `-c copy` สำหรับ segments, audio fade 30ms
- Output: `video_projects/<name>/edit/base_preview.mp4`

ใช้ `scripts/render.py` เป็น starting point

---

### Step 4 — Captions (Hyperframes)

ดู `CAPTION_PHILOSOPHY.md` สำหรับ spec ครบ สรุป:

```bash
# Install component (ครั้งแรก)
npx.cmd hyperframes add caption-highlight

# Lint ก่อน render เสมอ
npx.cmd hyperframes lint --verbose   # ต้องได้ 0 errors

# Render
npx.cmd hyperframes render --format webm -o render.webm
```

- Font: **Noto Sans Thai 800** เท่านั้น
- Canvas: 1080×1920, `bottom: 360px`, `font-size: 64px`, maxWidth 984px
- Thai words via `pythainlp` ด้วย proportional timing
- ใช้ `scripts/gen_composition.py` เป็น template

---

### Step 5 — Composite

```bash
ffmpeg \
  -i base_preview.mp4 \
  -vcodec libvpx-vp9 -i animations/slot_captions/render.webm \
  -filter_complex "[0:v][1:v]overlay=0:0[v];[0:a]loudnorm=I=-14:TP=-1:LRA=11[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 20 -c:a aac -b:a 192k \
  final.mp4
```

> `-vcodec libvpx-vp9` บน WebM input เป็น **บังคับ** — ถ้าไม่ใส่ alpha channel หายไปทั้งหมด

---

### Step 6 — BGM (ถ้ามี)

ดู `AUDIO_PHILOSOPHY.md` — mix ที่ **8% volume** เสมอ ไม่ต้องถาม user

---

## Directory Structure

```
raw_media/                        ← footage ต้นฉบับ (ห้ามแก้ไข)
video_projects/
  <name>/
    edit/
      <name>_transcript.json
      edl.json
      base_preview.mp4
      animations/
        slot_captions/
          index.html
          render.webm
      final.mp4
      final_bgm.mp4               (ถ้ามี BGM)
```

---

## Non-Negotiable Rules

1. **Propose cuts → รอ confirm → ค่อยเขียน EDL** ไม่มีข้อยกเว้น
2. **`-vcodec libvpx-vp9`** บน WebM ทุกไฟล์จาก hyperframes
3. **`npx.cmd`** ไม่ใช่ `npx` ใน PowerShell (`.ps1` ถูก block โดย execution policy)
4. **`PYTHONUTF8=1`** และ **`PYTHONIOENCODING=utf-8`** ก่อน run Python ทุกครั้ง
5. **Noto Sans Thai 800** เท่านั้น — Leelawadee UI ใช้ใน headless Chromium ไม่ได้
6. **Subtitles ทีหลัง** — composite หลัง base ได้รับ confirm แล้ว
7. **Loudnorm บน composite output** ไม่ใช่บน base_preview
