# Hardware and cost routing — 2026-10-12
- GTX 1050 Ti: typically 4GB dedicated VRAM (verify exact card locally); do not plan modern diffusion video inference on it.
- Mac mini M4 base: 10-core GPU, base 16GB unified memory; 256GB storage reported by owner. Use for orchestration, preflight, FFmpeg, image layers and possibly tiny image-model experiments **only after measurement**.
- Codex subscription quota is NOT a generic GPU inference credit. No payment API credentials configured.
- Default routing: script/validation: local + existing coding quota; keyframe: deterministic diagrams/editable source locally, expensive generative refinement opt-in; clip: 2D pan/zoom/layer animation local, demanding generative I2V cloud on explicit approval.
- Preview contract: low-cost storyboard / animatic before any paid inference; do not use high-quality generative video to test a script.
- Production cost formula: total = cloud GPU rental hours * hourly price + paid image/video requests + storage/transfer. Quotes must be checked at purchase time.
- Indicative **planning ceilings, not provider price quotes**: monthly external inference target RMB 0 during infrastructure; pilot discretionary cap RMB 50–100 only if approved; formal cap set after 3 representative shots and measured cost/accepted second.
- Never silently buy credits, invoke billable APIs, or expose local services publicly.
- Official Wan2.2 repo lists TI2V-5B as >=24GB VRAM with offload; A14B regular inference around >=80GB. Low-VRAM community quantizations are experimental and not a production promise.
Source: https://github.com/Wan-Video/Wan2.2 and https://support.apple.com/en-us/121555
