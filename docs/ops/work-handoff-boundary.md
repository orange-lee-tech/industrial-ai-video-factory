# GitHub / Work / Codex collaboration boundary

Work currently handles the pilot's script and keyframe packaging on its own workstream. This infrastructure branch is intentionally based on main and does **not** edit PR #1/#2 pilot files. Do not cherry-pick unreviewed PR changes blindly.

| Actor | Owns | Does not automatically do |
|---|---|---|
| ChatGPT / Work | factual research and references, script revisions, keyframe brief, repository planning and deterministic files | attest industrial accuracy without evidence; buy model calls |
| Codex (if needed) | local tooling integration, repeatable media pipelines, dependency testing, rendering execution | re-invent approved knowledge/visual choices |
| Human expert | engineering accuracy, difficult visual claims, cost approval, copyright/source assessment | hand-copy assets between devices |

## Handoff contract
1. Provide repo + branch + exact commit, source artifact location and schema version.
2. State **what is verified** and **what still requires review**; include test command and output evidence.
3. Identify only the next blocked step (not a giant speculative roadmap).
4. Use one active producer per shared file/branch. Merge through PR and reconcile conflicts, never overwrite a concurrent Work result.
5. Favor standard formats (JSON, PNG, SVG, MP4, Markdown) and interchangeable compute providers.
