# Contract v0.1
Single active production job, stage-gated. No model invocation is implicit.
Stages: script -> keyframes -> clips -> assembly (optional).
Each stage is APPROVED only by explicit human review; local automated checks are necessary but not sufficient.
Manifest fields are stable IDs. A downstream artifact carries upstream_sha256, allowing invalidation after edits.
No secrets, raw proprietary drawings, copyrighted material without authorization, or model weights in Git.
