# Industrial AI Video Factory

以**真实成片质量**而不是自动化脚本数量衡量结果的工业科普视频生产项目。**唯一持续开发分支：`main`**；中南大学《凝汽器与真空系统》26 镜、158 秒是当前课程交付试样。

## 2026-10-12 当前结论（必读）
**ChatGPT Plus 可以辅助研究、脚本、分镜和高质量静态关键帧，但 Plus / Work / Codex 并不能保证独立完成自然运动、工业准确的 158 秒完整视频。** Plus 不等于无限视频生成额度。不得把编程、FFmpeg 编码成功、像素变化或滑动贴图误报为合格动画。

已制作六张较好的 PNG（SH003、SH007–SH011），可作视觉候选；两轮 SH009–SH011 18 秒自制动态样片均被人眼拒绝：第一次近似幻灯片，第二次为不自然的图层/纹理平移。**停止继续修补该路线**。迄今没有经人工通过的动态试产或完整成片。

**新生产原则：**主题/受众 → 叙事与事实脚本 → **同时设计画面与运动的分镜** → 按镜头选取适当资产及后端（参考帧图生视频、独立二维动画或三维场景）→ 动态镜头自然度和专业事实双验收 → 配音/字幕/音乐/剪辑 → 全片验收。**不强制每镜 SVG，不强制 PNG→动图，不强制代码平移。**

**预算：零新增付费优先。** 探索 Plus 已有权益、可用的免费试用/演示或已有设备；实际免费额度并不保证。未经用户明确同意不得购买服务、启动收费 API 或云 GPU。先做一个低成本真实动态镜头验证，再决定是否扩批。

- [最新能力判断与工作流纠偏（最高优先级）](docs/decisions/2026-10-12-video-capability-and-pivot.md)
- [规范权威、分支和维护](docs/MAINTENANCE.md)
- [最新 Work/Codex 交接](docs/ops/work-handoff-boundary.md)
- [逐镜方法与后端说明](docs/architecture/render-backend-contract.md)
- [试产历史和失败样本](projects/csu-condenser-158s/README.md)
- [关键帧规范（静态视觉专用）](docs/production/keyframes-v1/alignment.md)

## 工作区
建议将真实媒体整理为 `01_策划与分镜/`、`02_镜头生产/`、`03_后期与交付/`、`99_历史与实验/`；它们是**工作区目录**，不是必须在 GitHub 重建的空目录。Git 管代码、规格和小文本，视频和敏感素材由单一工作区管理。

## 自动化测试
```bash
python -m unittest discover -s tests -v
python scripts/validate_project.py projects/demo-smoke/project.json
```
代码测试 **不等于** 实际视频自然度、工业知识或完整成片通过。

## 第三方授权
自有代码由根目录 LICENSE 约束；其他 Skill、图像、字体、模型、TTS 和生成平台依各自许可。 `director-storyboard` 暂缓； `anything2explainer` 仅研究其工程方法（PolyForm Noncommercial，没有整包复制）。
