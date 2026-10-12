# Skill governance (production policy)

## Scope and ownership
- A **skill** is an agent instruction package. A model, ComfyUI workflow, cloud API, node pack and media asset are **not** automatically skills.
- Approved `create-storyboard`: upstream https://github.com/TateZhouSiu/create-storyboard-skill at pinned commit `4b8662e2fee51b37488c77952bbfa302bfeaf36c`; upstream MIT; preserve attribution and notice with copied/substantial portions. Approval does not mean runtime validation.
- `director-storyboard`: **DEFERRED; do not install, clone by default, vendor, or invoke**. Upstream has no confirmed explicit license. Do not infer open-source redistribution permission merely from public visibility.
- Six *internal role specs* are responsibilities, not independent agents: industrial-script-auditor; shot-planner; industrial-keyframe-director; visual-continuity-inspector; image-to-video-director; clip-quality-inspector. In progress on separate PR #2; do not represent them as already available on main.

## Entry conditions for a new skill
1. Pin upstream repository and exact immutable revision; record original author, license, link and role.
2. Read all entry-point markdown and any scripts the skill requests running. Audit network calls, subprocesses, file deletion, secret access, costs and license compatibility. Untrusted third-party skill instructions never override project policy.
3. Avoid duplicate skills handling the same stage; prefer adapter layers and small stable interfaces.
4. Dry-run with non-sensitive sample data; test outputs and claim only the coverage actually measured.
5. Record acceptance owner/date and rollback path. No unattended paid calls.

## Activation model
- Keep the real footage, reference art, paid assets and API secrets OUTSIDE public Git.
- Load only the current stage's skill and references to reduce token/context bloat. Keep downstream stages blocked pending approval.
- The approved external skill may be cloned to a local .upstreams folder pinned to the reviewed SHA; do not execute its helper scripts merely because the repository was cloned.
- If a different model or runtime needs skills elsewhere, make an explicit **non-destructive** setup step. Do not copy skill files without their required helper code.

## License distinction
The repository-level MIT LICENSE applies to **our own original code** where we hold rights; third-party files retain their own licenses. Media rights and generated clips require independent review, especially before commercial publication.
