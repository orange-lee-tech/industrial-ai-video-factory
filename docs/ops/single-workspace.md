# One workspace, minimal operations

## Principle
A single canonical production **workspace** and project manifest, not necessarily a single physical computer or a permanent server. Keep management simple and select compute (local, SaaS, rental GPU) by accepted output quality, cost, convenience, license, and future commercial suitability.

## Separation of concerns
- GitHub: source code, roles, workflow descriptions, schema, small examples, PR reviews and tests. **Never the renderer or bulk media store.**
- Workspace: canonical job manifests, evidence, approved source geometry, stills, video, generation logs, approved output and immutable input checksums.
- Execution backend: optional service. May be local or cloud; must return artifacts into the same workspace (automated transfer/registration, not user hand-carry).
- Human: approves industrial truth and visually critical outputs. An automated JSON validator is not an expert reviewer.

## Minimal job layout
```
<workspace>/<project-id>/
  source/             # private source, licensing evidence
  manifest.json       # current state + dependencies
  knowledge/          # citations and unresolved claims
  script/             # reviewed voiceover, visual claim list
  reference/          # canonical equipment schematic + equipment IDs
  keyframes/          # per-shot approved source stills
  clips/              # generated silent clips
  reviews/            # checklists with approval and reviewer
  outputs/            # optional edited master
```
Folders are a convention, not an instruction to generate placeholders and claim delivery.

## State and invalidation
DRAFT → REVIEW → APPROVED → LOCKED. Downstream only consumes approved and content-addressed upstream outputs. Editing a script or equipment topology invalidates dependent keyframes and clips; independent shots need not be regenerated. Always capture prompt, model/backend version, input digests, cost, parameters, output locations and QA decision.

## First proof: CSU condenser and vacuum system
Scope: 26 shots, 158 seconds. Get engineering review of all narration and diagrams; lock a canonical condenser reference (cooling water INSIDE tubes, exhaust steam OUTSIDE tubes) before image generation; trial representative SH003 and SH007–SH011 keyframes; animate a few representative clips; measure accepted seconds per cost before committing to an entire video. End card/subtitles remain independently editable.

## Avoid until justified
No dedicated GPU purchase, permanent cloud GPU, NAS, Kubernetes, multiple local clones of media, enterprise queues or bespoke video editor needed for the first pilot.
