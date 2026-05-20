# Claude Thai Video Editing Studio

ตัดต่อวิดีโอภาษาไทยผ่านการสนทนากับ Claude Code

วาง footage ไว้ใน `raw_media/` → บอก Claude → ได้ `final.mp4` พร้อม karaoke subtitle และ loudnorm ครบ

---

## สิ่งที่ Studio นี้ทำได้

- **Transcribe ภาษาไทย** — ElevenLabs Scribe ด้วย character-level timestamps
- **ตัดต่ออัตโนมัติ** — ตัด dead air, filler, stutter โดย Claude เสนอ cut plan ก่อนแล้วรอ confirm
- **Karaoke Subtitle** — per-word highlight ด้วย hyperframes (caption-highlight component)
- **Audio Mastering** — loudnorm −14 LUFS มาตรฐาน TikTok/Reels
- **BGM Mixing** — mix BGM อัตโนมัติที่ 8% volume

รูปแบบ: สัมภาษณ์ testimonial แนวตั้ง **1080×1920 (TikTok / Reels)**

---

## Prerequisites

ติดตั้งทั้งหมดก่อน แล้วค่อย clone repo

### 1. Claude Code

ดาวน์โหลดที่ [claude.ai/code](https://claude.ai/code) (Desktop App สำหรับ Windows)

หรือติดตั้งผ่าน npm:
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Node.js 22+

ดาวน์โหลดที่ [nodejs.org](https://nodejs.org/) — เลือก **LTS version**

ตรวจสอบ:
```powershell
node --version   # v22.x.x หรือใหม่กว่า
```

### 3. Python 3.11+

```powershell
winget install Python.Python.3.12
```

หรือดาวน์โหลดที่ [python.org](https://www.python.org/downloads/)

ตรวจสอบ:
```powershell
python --version   # Python 3.11.x หรือใหม่กว่า
```

### 4. uv (Python package manager)

```powershell
winget install astral-sh.uv
```

หรือ:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

ตรวจสอบ:
```powershell
uv --version
```

### 5. ffmpeg (full build พร้อม libvpx)

> **สำคัญ:** ต้องใช้ full build เท่านั้น (มี libvpx-vp9 สำหรับ alpha overlay)
> ห้ามใช้ ffmpeg จาก winget ทั่วไปเพราะไม่มี libvpx

```powershell
winget install Gyan.FFmpeg
```

หรือดาวน์โหลด **ffmpeg-release-full** ที่ [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
แตกไฟล์แล้ว add ไปที่ PATH

ตรวจสอบ (ต้องเห็น libvpx-vp9):
```powershell
ffmpeg -encoders | findstr vpx
```

### 6. ElevenLabs API Key

สมัครที่ [elevenlabs.io](https://elevenlabs.io/) → Settings → API Keys → Create API Key

---

## Quick Start

```powershell
# 1. Clone repo
git clone https://github.com/<your-username>/Claude-Thai-Video-Studio.git
cd Claude-Thai-Video-Studio

# 2. ตั้งค่า API key
cp .env.example .env
# เปิดไฟล์ .env แล้วใส่ ELEVENLABS_API_KEY=sk-...

# 3. เปิด Claude Code ใน folder นี้
claude
```

เมื่อ Claude Code เปิดขึ้นมา **paste setup prompt นี้ลงไปเลย:**

```
Setup this Thai Video Editing Studio workspace. Install hyperframes and all required dependencies.
```

Claude จะติดตั้ง hyperframes และ dependencies ทั้งหมดให้อัตโนมัติ

---

## วิธีใช้งาน

### ตัดต่อวิดีโอใหม่

1. วาง footage ใน `raw_media/` (MP4, MOV, ฯลฯ)
2. พิมพ์ใน Claude Code:

```
ช่วยตัดต่อ raw_media/ชื่อไฟล์.mp4 ให้หน่อย
```

Claude จะทำทุกอย่างให้:
- Transcribe ด้วย ElevenLabs
- เสนอ cut plan → รอ confirm → ตัด
- ทำ karaoke subtitle
- Render + loudnorm

### คำสั่งที่ใช้บ่อย

```
# ตัดต่อวิดีโอ
ช่วยตัดต่อ raw_media/interview.mp4

# ดู cut plan ก่อน
transcript เสร็จแล้ว เสนอ cut plan ได้เลย

# เพิ่ม BGM
เพิ่ม BGM จาก BGM.mp3 ให้ด้วย

# แก้ subtitle
ช่วย re-render subtitle ใหม่โดยลดจำนวนคำต่อกลุ่มลง
```

### Output

```
video_projects/
  interview/
    edit/
      interview_transcript.json   ← transcript ภาษาไทย
      edl.json                    ← cut list
      base_preview.mp4            ← ตัดแล้ว ยังไม่มี subtitle
      animations/
        slot_captions/
          index.html              ← composition
          render.webm             ← subtitle overlay
      final.mp4                   ← ✅ ไฟล์สำเร็จ
      final_bgm.mp4               ← ✅ พร้อม BGM (ถ้ามี)
```

---

## โครงสร้าง Repo

```
Claude-Thai-Video-Studio/
│
├── 📁 raw_media/                    ← วาง footage ที่นี่
│
├── 📁 video_projects/               ← Claude สร้าง project ที่นี่
│   └── <ชื่อโปรเจค>/
│       └── edit/
│           ├── *_transcript.json
│           ├── edl.json
│           ├── base_preview.mp4
│           ├── animations/slot_captions/
│           └── final.mp4
│
├── 📁 scripts/
│   ├── render.py                    ← render base preview จาก edl.json
│   └── gen_composition.py           ← generate hyperframes HTML
│
├── 📁 .claude/
│   └── settings.json                ← permissions สำหรับ Claude Code
│
├── CLAUDE.md                        ← ⭐ Instructions หลักของ Claude
├── THAI_CONTENT_PHILOSOPHY.md       ← หลักการตัดต่อภาษาไทย
├── CAPTION_PHILOSOPHY.md            ← ระบบ subtitle + bugs ที่รู้แล้ว
├── AUDIO_PHILOSOPHY.md              ← loudnorm + BGM
│
├── .env.example                     ← template API keys
├── .env                             ← API keys จริง (gitignored)
└── .gitignore
```

---

## Pipeline ภาพรวม

```
raw_media/video.mp4
        │
        ▼ ElevenLabs Scribe
transcript.json  (character-level timestamps)
        │
        ▼ reconstruct_words() + pythainlp
per-word timing
        │
        ▼ propose cuts → user confirms
edl.json
        │
        ▼ scripts/render.py
base_preview.mp4  (ตัดแล้ว, CRF 22)
        │
        ▼ scripts/gen_composition.py → hyperframes render
render.webm  (VP9 alpha subtitle overlay)
        │
        ▼ ffmpeg composite + loudnorm −14 LUFS
final.mp4  ✅
        │
        ▼ (optional) BGM 8% mix
final_bgm.mp4  ✅
```

---

## คำสั่ง Scripts (manual)

ถ้าต้องการ run เอง:

```powershell
# ตั้งค่า environment ก่อน (PowerShell)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# Render base preview จาก EDL
uv run scripts/render.py video_projects/myproject/edit/edl.json

# Generate subtitle HTML
uv run --with pythainlp scripts/gen_composition.py `
  video_projects/myproject/edit/myproject_transcript.json `
  video_projects/myproject/edit/edl.json `
  video_projects/myproject/edit/animations/slot_captions

# Lint subtitle (ต้อง 0 errors ก่อน render)
cd video_projects/myproject/edit/animations/slot_captions
npx.cmd hyperframes lint --verbose

# Render subtitle overlay
npx.cmd hyperframes render --format webm -o render.webm
```

---

## ติดปัญหา?

ถาม Claude โดยตรงใน Claude Code ได้เลย — Claude รู้ context ของ repo นี้ทั้งหมด

---

## Philosophy Docs

| ไฟล์ | เนื้อหา |
|------|---------|
| [CLAUDE.md](CLAUDE.md) | Pipeline หลัก 6 ขั้นตอน + กฎที่ห้ามละเมิด |
| [THAI_CONTENT_PHILOSOPHY.md](THAI_CONTENT_PHILOSOPHY.md) | สไตล์คอนเทนต์, transcript handling, cut decisions |
| [CAPTION_PHILOSOPHY.md](CAPTION_PHILOSOPHY.md) | Hyperframes spec, Thai adaptations, VP9 bug, ๆ bug |
| [AUDIO_PHILOSOPHY.md](AUDIO_PHILOSOPHY.md) | Loudnorm −14 LUFS, BGM 8% |

---

## Credits

Inspired by [Claude-Video-Editing-Studio](https://github.com/captainp369/Claude-Video-Editing-Studio)
Built for Thai short-form content production
