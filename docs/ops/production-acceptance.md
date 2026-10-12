# Practical gate checklist — not a claim of completed validation

> **2026-10-12 历史适用范围说明：** 本文中要求继续生成 PNG、试产 18 秒本地确定性动画、或者派 Work 施工的段落属于先前阶段的记录，**当前不再自动授权执行**。最新有效规则见 [视频能力判断及生产流程重置](../decisions/2026-10-12-video-capability-and-pivot.md)。两个本地动画试产均经用户 FAIL；停止素材平移返工。关键帧仅为可选静态资产；首先验证自然动态视频生成，零新增付费优先。



Current still-frame authority: docs/production/keyframes-v1/. SVG is optional, direct high-quality PNG mandatory. These operational lists do not define an alternative image status or delivery contract; use alignment.md for state mapping and the per-shot double-review records.
## Script gate (mandatory)
- [ ] 26 narration entries mapped to 158-second condenser pilot; intended output at least 120 seconds.
- [ ] Each technical claim has source/reviewer or explicit uncertainty.
- [ ] Condenser internal geometry, vacuum terminology, cooling-water and condensate separation correct.
- [ ] Specific extraction technology described as an example unless backed by equipment reference.

## Image gate (mandatory)
- [ ] Canonical approved condenser equipment map and perspective stable over dependent shots.
- [ ] In-/out-of-tube flow distinction stable; no invented piping or equipment.
- [ ] Generated visual source images contain no AI-rendered labels; overlay Chinese text deterministically.
- [ ] Record approved exact file path, dimensions, hash, dependencies and reviewer.

## Clip gate (mandatory)
- [ ] Freeze frame comparisons at entry/mid/exit show no topology drift.
- [ ] Actual video file exists and ffprobe verifies duration/fps/codec.
- [ ] No impossible medium flow, flashing or spurious text. Approval explicitly recorded.

## Optional assembly gate
- [ ] Total timeline, captions, end card, readable typography, music rights and commercial-use terms assessed.
- [ ] Final master truly exported and locally played, not just a project file.

## Economic evaluation
Record spend / total generated seconds / **approved usable seconds** / retries / human minutes / model license and artifact retention. Choose a backend only after representative trials; no assumption that cloud or local always wins.
