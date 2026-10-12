# Decision record — 2026-10-12

## Director-storyboard
Status: **DEFERRED / DO NOT INSTALL / DO NOT VENDOR**.
Upstream: https://github.com/ai2764/ai-video-skills
Reason: no explicit upstream license identified in prior review; not needed for immediate condenser video pilot. Earlier approval to investigate is superseded. This is an archival candidate only. Do not clone, install, run, copy, or require it in the active workflow unless the user explicitly reopens this decision and license/use conditions are clarified.
Any older PR scripts or registries that still list it as approved or offer `-WithUpstreams` are **historical and must be corrected before use or merge**.

## Runtime / equipment
Policy: **cloud-neutral, minimum operational complexity**. No fixed commitment to T470s, F117, or Mac mini as the production machine. Optimize for accepted-video quality, time to delivery, total spend (model calls, storage, network, maintenance, labor), ease of upgrade, and future commercial operation.
For the first 158-second CSU condenser pilot:
1. Keep one canonical project workspace and machine-readable handoffs. GitHub is source-code/spec/version control, not the media rendering or storage system.
2. Prefer a managed cloud image/video generation service when total cost and management are favorable; local is allowed for text, review, deterministic drawing/assembly, or where demonstrably cheaper.
3. Do not provision a fleet, permanent GPU host, cross-device manual copy workflow, or self-host ComfyUI just for theoretical flexibility.
4. Maintain a minimal backend interface and ability to export all approved frames, clips, prompts, parameters and manifests in ordinary file formats.
5. Never assume cloud is cheaper: compare actual quote and test a few representative clips before selecting. No paid action without prior user authorization.
6. First priority is a technically correct script and usable SH003/SH007–SH011 keyframes, then short clip tests and finally the full 158-second deliverable.
7. Keep media and credentials private; use remote storage only when required, with access control, clear data retention policy and IP licensing suitable for eventual commercialization.

## Priorities
Maintain six *logical* role boundaries only as useful quality gates. Avoid treating each role as separate infrastructure. Minimize project bureaucracy and up-front buildout.
