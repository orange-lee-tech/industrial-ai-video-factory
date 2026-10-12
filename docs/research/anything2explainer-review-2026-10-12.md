# anything2explainer — technical review and adaptation decision

Upstream: https://github.com/Vincentwei1021/anything2explainer, reviewed at commit `735c79c8724e897e8971cd59dde7e5aa11e4d6ce`.
Project skill: `SKILL.md`, `reference/composition-and-light.md`, `reference/research-brief.md`, `reference/agent-qc-rules.md`, `examples/rag/`.
License: **PolyForm Noncommercial 1.0.0**, including required author notice; bundled fonts SIL OFL; Remotion independently licensed. It is **not** MIT. Public GitHub does not imply free commercial redistribution or operation.

## What was validated
- A genuine project template / source-controlled frames approach: React + Remotion with per-shot frame-driven components; narration and render helpers; structured research, narration, storyboard, build, QC and repair passes.
- The `RAG 与知识库` content is a **sample video topic**, not an installed RAG retrieval server or a vector index.
- Four approval checkpoints: duration/language, narration lock, TTS engine, first 30-second look validation.
- Valuable lessons: source citations for claims; one visual lead per shot; edited information hierarchy; per-shot continuity; programmable motion; preflight and preview; frame sampling and regression inspection.
- Limits: highly distinctive black/purple template, code-first diagrams do not guarantee correct condenser geometry; Chinese TTS is an external endpoint; builds may involve many parallel agents / Codex token use; renderer and bundled fonts have separate licenses.
- The reference project's source code is **not** vendored here. This repository's new code and documents are authored independently and do not use upstream graphics, prompt templates, QC script implementation or protected expression.

## Admission policy
`candidate / reviewed / method-adopted / upstream-not-installed / commercial-authorization-needed`.
We can apply high-level methods and independently write compatible interfaces. For direct use of PolyForm-protected toolkit in **noncommercial** CSU teaching pilot, comply with license and notices; if intended for later commercial use, obtain author permission before running that toolkit commercially. Do not relicense their code under this repo's MIT. For commercial operation, use independently authored Remotion components or another permitted stack; verify Remotion licensing separately.

## Decisions
1. Use a **deterministic motion-graphics backend candidate** in parallel with optional generative I2V, not a mandated single backend.
2. Preserve `approved equipment geometry -> visual composition -> shot plan -> silent clip -> QA` stage gates.
3. Avoid requiring TTS for the pilot. Current 158s timeline is locked; do not auto-rewrite it by voice timing. Overlay labels/subtitles remain deterministic and editable.
4. Gate one high-quality SH007 art keyframe and a 6s motion test before producing the rest. User's B+ / possible C is authoritative, not the upstream project's fixed style.
5. Use QC for objective media properties, staging, motion, flow continuity; always keep expert fact and visual approvals manual.
6. Avoid premature RAG vector infrastructure. Store source IDs, citations, claims and uncertainties first. Add retrieval only if corpus size/search accuracy demonstrates a need.
7. Compare cost per approved second including agent/token, GPU, render, corrections, labor, copyright and hosting.

## Missing verification
No upstream install or rendered comparison on current hardware; no claimed proof of their sample's reproducibility. No derivative copying permitted under the project's default MIT.
