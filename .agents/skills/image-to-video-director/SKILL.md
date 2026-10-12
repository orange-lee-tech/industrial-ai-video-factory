---
name: image-to-video-director
description: Turn approved image references into 6 second silent clips, with deterministic fallback and optional model adapter.
---
# Image to Video Director
Use upstream .upstreams/ai-video-skills/codex/director-storyboard/SKILL.md only when its full repo and helpers are present. That upstream targets LTX/H3 timeline; **adapt per-shot** (do not stitch unrelated industrial geometries in a hallucinated continuous clip). Input approved keyframes and motion specification. Default dry-run, no paid model calls. For simple maps/particles/zoom prefer deterministic layered animation. Log backend parameters and preserve input image immutably. Output is silent clip and run manifest, not audio/subtitles.
