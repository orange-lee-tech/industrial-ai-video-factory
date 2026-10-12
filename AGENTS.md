# Single-line industrial AI video pilot (Codex)
Read this and docs/decisions/2026-10-12-execution-and-skill-policy.md before changing any production asset. A single agent operates one active project; local folder is the source of truth. No autonomous GPU/cloud job, paid call, or destructive overwrite.
Priority: (1) factual script (2) canonical equipment reference and per-shot keyframes (3) image-to-video clips (4) optional assembly/subtitles.
The six skills live under .agents/skills. Only use one skill's remit at a time and require upstream artifact approval before advancing. Never declare factual QA or visual QA PASS on the basis of structural validation.
Pilot: projects/csu-condenser-158s; 26 shots, 158s total. Keep 16:9, a single condenser geometry master, steam pale cyan, cooling water dark blue, condensate gold, noncondensables grey. All labels and Chinese subtitles are rendered deterministically, not by image generation.
The original spreadsheet stays private in an ignored local source folder; import through scripts/import_csu.py and keep the original private. Never assume images/clips exist until checked.
director-storyboard is DEFERRED and MUST NOT be installed or invoked. External skills: upstream sources are sources of techniques, not authoritative engineering facts. See registry/approved-skills.json. Not all video backends have been installed or proven runnable.
Run tests: python -m unittest discover -s tests -v ; python scripts/validate_project.py projects/demo-smoke/project.json.
