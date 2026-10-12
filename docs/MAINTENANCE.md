# Canonical repository operating rules (consolidated 2026-10-12)

**main is the only ongoing development branch.** Open short-lived feature branches only when making changes; merge immediately after validated review, then delete when safe. `archive/csu-condenser-158s` is a read-only reference snapshot, NOT an active production branch. Real renders and private source work live outside Git in one canonical workspace.

## Authority hierarchy
1. `00_constitution/production-principles-v1.md` — product invariants.
2. `docs/decisions/2026-10-12-execution-and-skill-policy.md` and `docs/decisions/2026-10-12-film-visual-route.md` — adopted constraints.
3. `contracts/` and executable validators — format and state gates.
4. `docs/ops/` — operational guide; `.agents/skills/` — six role instructions.
5. `projects/csu-condenser-158s/` — **pilot example**, not a second global policy.

If lower levels disagree with higher levels, fix the lower level; never silently maintain competing standards.

## Skills
- `create-storyboard` is approved as a pinned, MIT-licensed upstream.
- `director-storyboard` remains **DEFERRED**, not a dependency; do not install, vendor or run.
- `anything2explainer` is **method-reviewed**, not vendored or installed. Its PolyForm Noncommercial license is separate from our MIT; commercial toolkit usage needs author authorization.
- Keep one skill owning each job responsibility. A backend (Remotion, cloud I2V) is not the same as a skill.

## Real status
- Structural tests and CI are not engineering fact approval, visual quality approval, nor proof of 158-second final video.
- SH007 is a film-art candidate, not signed-off quality; the uploaded ZIP is not the repository's source-of-truth rendered video.
- Never execute paid jobs without explicit spend approval.
- Validate after each integration: `python -m unittest discover -s tests -v`; for the real pilot follow `docs/ops/production-acceptance.md`.
