---
name: image-to-video-director
description: Turn approved image references into 6 second silent clips, with deterministic fallback and optional model adapter.
---
# Image to Video Director
director-storyboard is DEFERRED by the latest project decision. Do not clone, install or invoke it. Use the implemented local backend contract instead. Input approved keyframes and motion specification. Default dry-run, no paid model calls. For simple maps/particles/zoom prefer deterministic layered animation. Log backend parameters and preserve input image immutably. Output is silent clip and run manifest, not audio/subtitles.

Local executable backends: python scripts/clip_runner.py --shot SH009 (dry-run default); --execute --preview creates explicitly unapproved draft animation without a model or network. Production --execute requires --approval binding script, master and both PNG hashes to a named reviewer. Backend choices are diagram-flow and still-pan; still-pan binds only its first image. Run manifest is content-addressed; inspect history before rerun.
