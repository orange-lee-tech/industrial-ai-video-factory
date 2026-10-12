# Decision: video capability boundary and production reset
Date: 2026-10-12
Status: **ACTIVE — supersedes prior default motion backend and pilot02 continuation orders**

## Facts observed
- ChatGPT Plus / Work / Codex were effective at research, writing, scripts, basic storyboarding and generating six good-looking static PNG candidates (SH003, SH007–SH011); industrial approval remains a separate gate.
- Neither Plus nor these orchestration/code tools guarantee professional natural-motion video generation, unlimited Sora/video inference, or delivery of a polished 158-second industrial film on their own.
- SH009–SH011 pilot01: 18-second MP4 had correct duration/frame parameters but was human-rejected as essentially static/slideshow. Frame differences inside shots were negligible versus scene cuts.
- pilot02: local layer/mask/texture translation introduced measured pixel motion but was **human-rejected as unnatural flat-image translation**. Programmatic movement is not automatically credible animation.
- A peer's approximately 125-second, 720p, 30fps AI video (reported cost tens of CNY, believed Jimeng or Kling, exact provenance unverified) provided stronger motion and spatial development, though with industrial-truth and generated-text risks. Do not represent its service or price as confirmed.
- Six film-art PNGs remain reusable assets. Historical SVGs and pilot render scripts are experimental reference, not accepted video output.

## First principles and corrected pipeline
Video communicates change and meaning over time, not merely a sequence of pretty stills. Storyboard must specify **what visibly changes, how objects move, what camera does, and how shots join**.
```
topic + audience + delivery requirements
 → narrative and verified script (optional scratch voice timing early)
 → motion-aware storyboard (events, camera, transition, constraints)
 → choose appropriate per-shot method and assets
 → produce actual dynamic shots (not mandatory PNG→GIF)
 → human review for naturalness AND industrial truth
 → edit shots, subtitles, narration, music, credits
 → end-to-end viewing and delivery
```
Keyframes are optional and task-dependent: reference first/last frames for video generation, layered assets for coded animation, or full 3D scene for complex spatial events. A flattened PNG does **not** contain hidden depth or an object-rig.

## Operating decision
1. **Stop** assigning iterative reworks to the current pan/mask pilot01/pilot02 pipeline; keep artifacts and reports as failures, not defaults.
2. Freeze speculative skill/CI/diagram infrastructure. Priority is the CSU course film (26 shots, 158 seconds, >2 min), not building a universal platform first.
3. Prefer zero **incremental** spend. Evaluate eligible existing plan entitlements, legitimately free video generation credits/demos, or existing equipment only where practical. Free tiers have quotas and uncertain availability; never imply unlimited usage. Never make a purchase, start a paid API, or allocate GPU rentals without specific user approval.
4. Choose video-generation vs coded animation vs 3D **per shot**. For natural cinematic movements, dedicated video generation is a candidate, not a proven deployed backend. Deterministic shapes remain helpful for accurate overlays/labels/flows; no mandatory SVG or raster-to-GIF step.
5. Technical tests, encoding, frame-difference metrics and file existence are **not** visual acceptance. Human reviews actual motion and factual constraints.
6. Make the cheapest possible end-to-end representative dynamic motion test before batch generation. Stop when approach is clearly wrong; do not repeatedly polish failed technique.
7. Preserve original student data and source licensing boundaries; no fabrication of commercial rights or expert signoff.
8. GitHub main is the sole active code authority; pilot records are documentation/example only.

## Status / restart conditions
- **Accepted:** keyframe PNGs as visual candidates; their final industrial approval is separate.
- **Rejected:** pilot01 static-look and pilot02 flat sliding motion; no accepted 18s dynamic test.
- **Not delivered:** final 158s video, approved motion backend, full professional/visual signoff.
- **Next permitted step:** compare no-extra-cost natural-motion generators and run a tiny SH003 device-camera test with user's participation where account access is needed, then optionally SH009 flow test. Do not direct Work to generate another DIY pan/mask animation.
- If tool can't generate credible shots without extra spend, report limitation and seek user decision instead of repeating failed implementation.
