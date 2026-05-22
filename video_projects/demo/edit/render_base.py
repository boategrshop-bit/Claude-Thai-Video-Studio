import json, subprocess, sys

FFMPEG = r"C:\Users\boate\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
BASE_DIR = r"D:\demo\Claude-Thai-Video-Studio\video_projects\demo\edit"

edl = json.load(open(f"{BASE_DIR}/edl.json", encoding="utf-8-sig"))
src = edl["source"]
segs = edl["segments"]
n = len(segs)

parts = []
for i, seg in enumerate(segs):
    s, e = seg["start"], seg["end"]
    dur = round(e - s, 6)
    parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];")
    parts.append(
        f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
        f"afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03:.6f}:d=0.03[a{i}];"
    )

concat_in = "".join(f"[v{i}][a{i}]" for i in range(n))
parts.append(f"{concat_in}concat=n={n}:v=1:a=1[vout][aout]")

filter_complex = "\n".join(parts)

cmd = [
    FFMPEG, "-y",
    "-i", src,
    "-filter_complex", filter_complex,
    "-map", "[vout]", "-map", "[aout]",
    "-c:v", "libx264", "-crf", "22", "-preset", "fast",
    "-c:a", "aac", "-b:a", "192k",
    f"{BASE_DIR}/base_preview.mp4"
]

print("Rendering base_preview.mp4 ...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-3000:])
    sys.exit(1)
print("Done: base_preview.mp4")
