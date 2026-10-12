# Interchangeable silent-video execution interface v0.1

The engine is selected **after** script approval and art keyframe approval, never automatically by a keyword in an unrelated prompt.

## Input `clip-job.json`
```json
{
  "schema_version": "0.1",
  "project_id": "csu-condenser-158s",
  "shot_id": "SH007",
  "duration_seconds": 6,
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "reference_asset": "keyframes/SH007-approved.png",
  "reference_sha256": "<actual 64-hex sha256 when approved>",
  "equipment_master_revision": "<approved revision>",
  "motion_spec": "gentle layer reveal, fixed tube bundle and waterboxes",
  "backend": "remotion-or-other-deterministic",
  "silent": true,
  "billing_approved": false
}
```
`reference_asset` is a workspace-relative path. Never place an invented digest or sample placeholder in a runnable production job.

## Output `clip-result.json`
```json
{
  "shot_id": "SH007",
  "status": "RENDERED_UNREVIEWED",
  "video_path": "clips/SH007.mp4",
  "backend_id": "name-and-revision",
  "input_sha256": "<computed sha256>",
  "video_sha256": "<computed sha256>",
  "render_seconds": 0,
  "cloud_cost_cny": 0,
  "quality_review": "PENDING"
}
```
Render attempts may fail; retain error, command (without secrets), logs and all intermediates. Only a human reviewer can promote media to `APPROVED`; `RENDERED_UNREVIEWED` is not `APPROVED`.

## Engines
- Deterministic SVG / React / Remotion / other coded animation: geometry-first, stable frame rendering, editable shapes, CPU render optional.
- Cloud generative image-to-video: only for approved immutable inputs, price and usage authorization checked per run; return to canonical workspace.
- Mix both in one film behind this exact clip interface. Editing only one shot invalidates only dependent shots.
- Enforce one project workspace and one task status; parallelism internal to individual eligible stages may be used later.
