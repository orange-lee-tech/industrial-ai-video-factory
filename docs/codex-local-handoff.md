# One-machine operator guide (Windows PowerShell / Mac terminal)
1. Clone the repo. Current integration branch may differ from main; use PR branch until approved.
2. Place the XLSX outside the repo (or in ignored local project/source after confirming ignore); do not publish raw class files unknowingly.
3. Windows: `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup_pilot.ps1 -WithUpstreams` from repo root. Mac: read setup notes and use git clone + checkout to exact approved SHAs; Python import is cross-platform.
4. `python scripts/import_csu.py 'path-to-file.xlsx'`; then `python -m unittest discover -s tests -v`.
5. Open Codex in repository root and ask it to read AGENTS.md and the six skill documents in .agents/skills. Only request script review and SH003/SH007–SH011 keyframe design first, not paid inference.
6. Both external skill repos are cloned as version-pinned source to .upstreams (ignored). The second upstream relies on its repository-root helpers, so **do not copy only SKILL.md**. External scripts are NOT automatically executed.
7. Local Mac M4 is the one control/asset workstation; cloud inference uses API adapters remotely later. Avoid device hopping, and never publish private LAN endpoints.
