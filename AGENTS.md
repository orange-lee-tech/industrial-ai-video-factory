# Industrial AI Video Factory — agent work contract

Read `README.md`, `docs/MAINTENANCE.md` and `docs/decisions/2026-10-12-video-capability-and-pivot.md` FIRST. `main` is the single active development branch. Execute only the authorized task; user is the production owner.

**Current pause:** The 18s SH009–SH011 local motion pilots have failed human review twice (slideshow; then flat texture/layer translation). Do NOT render pilot03, tweak pan/mask effects, continue the pilot02 scripts, or begin 20-shot batch production on your own. Keep existing six PNGs and test evidence. No accepted full film.

The first-principles sequence is: topic/audience -> verified script -> motion-aware storyboard -> choose assets/backend for each shot -> real dynamic shot -> independent naturalness/factual review -> edit/narration/subtitles/music -> full-film human QA. Flattened PNGs don't automatically provide parallax, depth, object rigs, fluid behavior. Technical file validity never implies acceptable video.

**No additional payment by default.** Don't run a billed API or rent compute without explicit authorization. Legitimate available free credits/Plus entitlements may be evaluated, but do not claim they are unlimited. If external accounts are inaccessible, request only the minimal human login/permission step.

Six internal skills are logical responsibilities, not a multi-agent mandate. Preserve accurate engineering facts, sources and human approvals; never label a technical check as professional accuracy or visual PASS. Historical local pan-flow scripts remain for reproducibility only, not active instructions.

Skills: `director-storyboard` DEFERRED; `anything2explainer` method-reviewed, not vendored; do not copy its PolyForm-protected toolkit into MIT repo. Keep project data and expensive media in private canonical workspace.

Test software separately: `python -m unittest discover -s tests -v`; `python scripts/validate_project.py projects/demo-smoke/project.json`.
