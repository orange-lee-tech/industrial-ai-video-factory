---
name: clip-quality-inspector
description: Inspect generated clips for shape drift, flash, medium flow reversal and artifact provenance.
---
# Clip Quality Inspector
Use ffprobe for duration/frame rate/size; sample start, middle, end frames with ffmpeg if installed; compare against approved reference. Flag tube morphing, falsely moving static metal, visually crossing water paths, flashing and AI text. No machine-only PASS for fluid/mechanical correctness. Approve the 26th shot as an 8-second end-card source only after overlay editor confirms content.

Read each run.json measurement and verify output SHA256. Inspect decoded start/middle/end frames. COMPLETED means a file was encoded, not clip approval. Record whether output is draft preview or professionally approved input awaiting clip review. Never approve silent previews as a finished narrated/subtitled film.
