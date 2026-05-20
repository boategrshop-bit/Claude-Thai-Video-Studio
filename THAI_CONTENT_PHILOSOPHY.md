# Thai Content Philosophy

## สไตล์คอนเทนต์

- รูปแบบ: testimonial สัมภาษณ์ host + นักเรียน/ลูกค้า
- Format: TikTok แนวตั้ง 1080×1920 (9:16)
- ผู้ชม: คนไทย บนแพลตฟอร์ม social (TikTok, Reels)
- Tone: เป็นธรรมชาติ พูดคุย ไม่ formal

---

## การจัดการ Transcript ภาษาไทย

### reconstruct_words() — บังคับ

ElevenLabs Scribe ให้ character-level tokens สำหรับภาษาไทย spacing token คือ
ตัวบ่งชี้ขอบเขตของคำ ต้องรวม characters เป็น word objects ก่อนทุกอย่าง:

```python
def reconstruct_words(characters):
    words = []
    current_chars = []
    current_start = None

    for ch in characters:
        if ch["character"] == " ":
            if current_chars:
                words.append({
                    "text": "".join(c["character"] for c in current_chars),
                    "start": current_start,
                    "end": current_chars[-1]["end"]
                })
                current_chars = []
                current_start = None
        else:
            if not current_chars:
                current_start = ch["start"]
            current_chars.append(ch)

    if current_chars:
        words.append({
            "text": "".join(c["character"] for c in current_chars),
            "start": current_start,
            "end": current_chars[-1]["end"]
        })

    return words
```

### ๆ token

`ๆ` (mai yamok) มักออกมาเป็น standalone token ต้อง merge เข้ากับคำก่อนหน้า
ก่อน chunking — ดู `CAPTION_PHILOSOPHY.md` สำหรับ bug detail

---

## Philosophy การตัด

### Dead Air
- Silence ≥ 0.4s → เสนอตัด
- Silence 0.2–0.4s → เสนอตัดถ้าไม่กระทบ natural pacing
- Pause สั้น < 0.2s → เก็บไว้ให้ดูเป็นธรรมชาติ

### Verbal Stutters
- คำซ้ำ/วลีซ้ำก่อนพูดประโยคหลัก (เช่น "ก็คือ ก็คือ...") → เสนอตัด
- Filler words ที่ไม่มีความหมาย (เช่น "อ่า", "เอ่อ") → เสนอตัด
- Filler words ที่ให้ความรู้สึก authentic → เก็บไว้ตาม context

### สิ่งที่ต้องเก็บ
- การหายใจระหว่างประโยค (natural pacing)
- Pause ที่ให้น้ำหนักกับ statement สำคัญ
- เสียงหัวเราะ/ปฏิกิริยา host และ guest

---

## Cut Plan Format (เสนอ user)

เสนอเป็น plain text ไม่ใช่ JSON:

```
ตัดได้ 4 จุด:
1. [0:03–0:05] "อ่า อ่า" (filler) — 2.1s
2. [0:12–0:14] หยุดยาว (silence) — 1.8s
3. [0:31–0:33] "คือ คือ คือ" (stutter) — 1.4s
4. [1:02–1:05] "เอ่อ..." ก่อนจบ (filler) — 2.7s

รวมตัด: ~8s จากคลิปยาว 1:45

ยืนยันก่อนจะเขียน EDL?
```

---

## EDL Format (edl.json)

```json
{
  "source": "../../raw_media/<name>.mp4",
  "segments": [
    { "start": 0.0,   "end": 3.0   },
    { "start": 5.1,   "end": 12.0  },
    { "start": 13.8,  "end": 31.0  }
  ]
}
```

## Base Preview Render

```bash
# สร้าง concat filter จาก segments
ffmpeg -i source.mp4 \
  -filter_complex "
    [0:v]trim=start=0:end=3,setpts=PTS-STARTPTS[v0];
    [0:a]atrim=start=0:end=3,asetpts=PTS-STARTPTS,afade=t=out:st=2.97:d=0.03[a0];
    [0:v]trim=start=5.1:end=12,setpts=PTS-STARTPTS[v1];
    [0:a]atrim=start=5.1:end=12,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.03,afade=t=out:st=6.87:d=0.03[a1];
    [v0][v1]concat=n=2:v=1:a=0[v];
    [a0][a1]concat=n=2:v=0:a=1[a]
  " \
  -map "[v]" -map "[a]" -c:v libx264 -crf 22 -c:a aac -b:a 192k \
  base_preview.mp4
```
