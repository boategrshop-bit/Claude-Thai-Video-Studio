# Audio Philosophy

---

## Loudnorm (บังคับทุกโปรเจค)

Standard สำหรับ TikTok / social media:

```
Target Loudness : -14 LUFS
True Peak       : -1 dBTP
LRA             : 11
```

ffmpeg filter:
```bash
-filter_complex "[0:a]loudnorm=I=-14:TP=-1:LRA=11[a]"
```

**Apply บน composite output เท่านั้น** — ไม่ใช่บน base_preview.mp4

---

## BGM Mixing (ถ้ามี)

Mix BGM ที่ **8% volume (volume=0.08)** เสมอ — ไม่ต้องถาม user

```bash
ffmpeg -i final.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.08[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]" \
  -map "0:v" -map "[a]" \
  -c:v copy -c:a aac -b:a 192k \
  final_bgm.mp4
```

> `-c:v copy` — ไม่ re-encode video อีกรอบ ประหยัดเวลาและ quality

---

## Audio Output Settings

| Setting | Value |
|---------|-------|
| Codec | AAC |
| Bitrate | 192k |
| Loudnorm | -14 LUFS / -1 dBTP / LRA 11 |
| BGM | 8% volume (0.08) |

---

## Pipeline Audio Order

```
Step 3: base_preview.mp4   ← audio จาก source เท่านั้น ไม่ loudnorm
Step 5: final.mp4          ← loudnorm applied ที่นี่ (composite)
Step 6: final_bgm.mp4      ← BGM added ถ้า user ขอ (optional)
```

ห้าม apply loudnorm ซ้อน (double loudnorm) — ทำครั้งเดียวที่ composite step
