# SFX Library — Free to use, no attribution required
Source: Mixkit (mixkit.co) — Mixkit License (free for commercial use)
CDN pattern: https://assets.mixkit.co/active_storage/sfx/{ID}/{ID}-preview.mp3

---

## transitions/ (6 files)
| File | Mixkit ID | Description |
|------|-----------|-------------|
| mixkit-fast-rocket-whoosh.mp3 | 1714 | Fast swoosh, great for quick cuts |
| mixkit-air-woosh.mp3 | 1489 | Soft air whoosh transition |
| mixkit-cinematic-whoosh-fast-transition.mp3 | 1492 | Sharp cinematic swoosh |
| mixkit-vacuum-swoosh-transition.mp3 | 1465 | Vacuum tube swoosh |
| mixkit-cinematic-tunnel-reverb-woosh.mp3 | 1486 | Deep reverb whoosh |
| mixkit-intro-transition.mp3 | 1146 | Smooth intro transition sweep |

## impacts/ (6 files)
| File | Mixkit ID | Description |
|------|-----------|-------------|
| mixkit-strong-punches-to-the-body.mp3 | 2198 | Body punch combo |
| mixkit-martial-arts-fast-punch.mp3 | 2047 | Fast karate-style hit |
| mixkit-impact-of-a-strong-punch.mp3 | 2155 | Single hard punch |
| mixkit-epic-impact-explosion.mp3 | 2782 | Epic distant explosion boom |
| mixkit-explosion-hit.mp3 | 1704 | Close-range explosion hit |
| mixkit-bomb-drop-impact.mp3 | 2804 | Heavy bomb/drop impact |

## comedy/ (5 files)
| File | Mixkit ID | Description |
|------|-----------|-------------|
| mixkit-cartoon-toy-whistle.mp3 | 616 | Slide whistle / comedy timing |
| mixkit-cartoon-laugh.mp3 | 2882 | Cartoon character laugh |
| mixkit-sad-game-over-trombone.mp3 | 471 | "Wah wah wah" fail trombone |
| mixkit-long-pop.mp3 | 2358 | Satisfying long pop |
| mixkit-cartoon-voice-laugh.mp3 | 343 | Voice laugh for comedy moments |

## ui/ (5 files)
| File | Mixkit ID | Description |
|------|-----------|-------------|
| mixkit-bell-notification.mp3 | 933 | Soft bell ding notification |
| mixkit-retro-game-notification.mp3 | 212 | 8-bit style notification |
| mixkit-modern-click.mp3 | 1120 | Clean UI click |
| mixkit-correct-answer-tone.mp3 | 2870 | Success / correct answer chime |
| mixkit-achievement-bell.mp3 | 600 | Achievement unlock bell |

## reactions/ (4 files)
| File | Mixkit ID | Description |
|------|-----------|-------------|
| mixkit-crowd-laugh.mp3 | 424 | Crowd laughing reaction |
| mixkit-audience-clapping.mp3 | 478 | End-of-show audience applause |
| mixkit-cheering-crowd.mp3 | 610 | Loud crowd cheer with whistle |
| mixkit-small-group-cheer.mp3 | 518 | Small group cheer and clap |

## cinematic/ (4 files)
| File | Mixkit ID | Description |
|------|-----------|-------------|
| mixkit-cinematic-drums-heartbeat.mp3 | 487 | Cinematic ancient drums (~39s) |
| mixkit-cinematic-swoosh-heartbeat.mp3 | 488 | Trailer swoosh + heartbeat |
| mixkit-game-show-suspense.mp3 | 667 | Game show suspense / waiting |
| mixkit-cinematic-whoosh-deep-impact.mp3 | 1143 | Deep impact cinematic whoosh |

---

## Usage in ffmpeg
```bash
# Mix SFX at specific time offset (e.g., add punch at 5.2s)
ffmpeg -i video.mp4 -i sfx/impacts/mixkit-martial-arts-fast-punch.mp3 \
  -filter_complex "[1:a]adelay=5200|5200[sfx];[0:a][sfx]amix=inputs=2:duration=first[a]" \
  -map "0:v" -map "[a]" -c:v copy -c:a aac output.mp4
```
