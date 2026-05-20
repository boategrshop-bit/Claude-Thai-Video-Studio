"""
render.py — Base preview renderer from edl.json
Usage: uv run scripts/render.py video_projects/<name>/edit/edl.json
"""
import json
import subprocess
import sys
from pathlib import Path


def build_filter(segments, source_duration=None):
    n = len(segments)
    fade_dur = 0.030  # 30ms audio fades

    video_parts = []
    audio_parts = []

    for i, seg in enumerate(segments):
        start = seg["start"]
        end = seg["end"]
        dur = end - start

        video_parts.append(
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]"
        )

        audio_filters = [
            f"atrim=start={start}:end={end}",
            "asetpts=PTS-STARTPTS",
        ]
        if i > 0:
            audio_filters.append(f"afade=t=in:st=0:d={fade_dur}")
        if i < n - 1:
            fade_out_st = max(0, dur - fade_dur)
            audio_filters.append(f"afade=t=out:st={fade_out_st:.3f}:d={fade_dur}")

        audio_parts.append(
            f"[0:a]{','.join(audio_filters)},asetpts=PTS-STARTPTS[a{i}]"
        )

    v_inputs = "".join(f"[v{i}]" for i in range(n))
    a_inputs = "".join(f"[a{i}]" for i in range(n))

    concat_v = f"{v_inputs}concat=n={n}:v=1:a=0[v]"
    concat_a = f"{a_inputs}concat=n={n}:v=0:a=1[a]"

    all_parts = video_parts + audio_parts + [concat_v, concat_a]
    return ";\n    ".join(all_parts)


def render(edl_path: Path):
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    source = Path(edl["source"])
    segments = edl["segments"]
    output = edl_path.parent / "base_preview.mp4"

    if not source.exists():
        # try relative to edl location
        source = edl_path.parent / edl["source"]
    if not source.exists():
        sys.exit(f"Source not found: {edl['source']}")

    filter_str = build_filter(segments)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(source),
        "-filter_complex", filter_str,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        str(output),
    ]

    print(f"Rendering {len(segments)} segments → {output.name}")
    subprocess.run(cmd, check=True)
    print(f"Done: {output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: uv run scripts/render.py <path/to/edl.json>")
    render(Path(sys.argv[1]))
