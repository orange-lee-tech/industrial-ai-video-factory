# Local skill access: no mandatory multi-device installation

This repo contains project policy; the practical pilot role files are currently proposed on PR #2. Until merged, clone/switch to that specific pilot branch and verify its contents before invoking any role. Avoid telling Codex to use files that are not on the checked-out branch.

## Approved external source (optional)
From the *production workspace host*:
```bash
git clone https://github.com/TateZhouSiu/create-storyboard-skill.git .upstreams/create-storyboard-skill
git -C .upstreams/create-storyboard-skill checkout --detach 4b8662e2fee51b37488c77952bbfa302bfeaf36c
```
Check the resolved revision via `git rev-parse HEAD`, review `skills/create-storyboard/SKILL.md`, then run only the scripts actually needed. On macOS/Linux and Windows with Git installed this works from the chosen project workspace. A clone alone does NOT register the skill globally with every Codex build; inspect your current Codex skill-discovery convention, then add a project-local link/junction only if needed. Keep upstream helpers reachable at their original relative paths. Default is no activation and no GPU/API invocation.

## Defer
`director-storyboard` is intentionally not installed. If you find it in an old branch setup script, stop and update that script or use a setup path limited to create-storyboard. See `docs/decisions/2026-10-12-execution-and-skill-policy.md`.

## License note
The first skill is MIT; keep its LICENSE with republished source. Cloning public code with no license does not grant broad redistribution rights. Record runtime and model API licensing separately from skill licensing.
