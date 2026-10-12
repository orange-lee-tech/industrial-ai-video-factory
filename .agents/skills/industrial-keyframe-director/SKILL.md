---
name: industrial-keyframe-director
description: Produce finished script-driven industrial PNG keyframes and per-shot provenance with separate fact and art gates.
---
# Industrial Keyframe Director
Read docs/production/keyframes-v1/alignment.md, the two V1 standards and the relevant main script/review entries. Use the reviewed script as factual text, source engineering claims from references/evidence.json, and use SH007 PNG as the visual-quality anchor. SVG is optional engineering aid, never a required per-shot deliverable or substitute for finished PNG.

For this user-authorized batch, reuse SH007 unchanged and generate SH003, SH008–SH011 with distinct whole-device/detail/macro composition. Output SH###_keyframe.png, SH###_brief.md, SH###_prompt.txt and SH###_provenance.json. Inspect actual full-size images and neighboring views. Record all parameters that are exposed; null plus explanation for unexposed model version/seed. Preserve failed attempts and repair only the failed constraint. No labels/arrows inside model-generated image; overlay later.

Follow image states SPEC_READY -> IMAGE_DRAFT -> FACT_REVIEW -> ART_REVIEW -> APPROVED -> MOTION_READY, with separate named human fact and art approvals. AI precheck and file validation cannot promote APPROVED. Stop after batch submission; no remaining-20 generation, no video, no paid API, no model download. The old deterministic renderer is internal geometry validation only.
