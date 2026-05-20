# Setup Prompt

หลังจาก clone repo และเปิด Claude Code ใน folder นี้แล้ว
**copy prompt ด้านล่างนี้ไป paste ใน Claude Code เลย:**

---

```
Setup this Thai Video Editing Studio. Do the following in order:

1. Check Node.js version (need 22+): node --version
2. Check uv is installed: uv --version  
3. Check ffmpeg has libvpx support: ffmpeg -encoders | grep vpx (or findstr vpx on Windows)
4. Install hyperframes globally: npx --yes hyperframes@latest --version
5. Add caption-highlight component: npx hyperframes add caption-highlight
6. Verify .env file exists with ELEVENLABS_API_KEY set (if not, remind me to copy .env.example to .env and fill in my key)
7. Run a quick sanity check and tell me what's ready and what still needs attention.
```

---

## หลัง Setup เสร็จ

วาง footage ใน `raw_media/` แล้วพิมพ์:

```
ช่วยตัดต่อ raw_media/ชื่อไฟล์.mp4
```

Claude จะจัดการทุกอย่างให้ครบ
