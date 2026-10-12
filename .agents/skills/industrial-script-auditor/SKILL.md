---
name: industrial-script-auditor
description: Validate industrial education script against sourced engineering facts before any visual production.
---
# Industrial Script Auditor
Input: source spreadsheet transcription, topic, verified equipment references. Output: `reviews/script-review.md` with each claim, source, severity and decision. Check steam/water paths, pressure terminology, typical vs universal designs, film vs dropwise condensation, phase change and energy balance. Mark UNKNOWN when no primary evidence. Never fabricate numeric operating values. Status REVIEW until a qualified human approves. For this pilot review 26 shots and target duration 158s.

Candidate output: projects/csu-condenser-158s/script/candidate.json and reviews/script-review.{json,md}; retain the actual source hash. Run python scripts/validate_pilot.py. Record evidence IDs and per-shot decisions. Write REVIEW, never self-sign approval. Draft planning requested by the user is permitted before professional signoff; production remains gated.
