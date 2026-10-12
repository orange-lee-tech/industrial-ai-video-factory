# Industrial AI Video Factory

工业级单线程 AI 视频生产流水线。主路径：**专业脚本（事实关卡） → 分镜及关键帧（视觉关卡） → 裸视频（动态关卡） → 可选配音字幕与剪辑**。

**唯一持续开发分支：`main`**。中南大学《凝汽器与真空系统》158 秒、26 镜是试产工程，不是本仓库唯一用途。实际大文件素材、渲染和付费生成发生在受控工作区，不在 GitHub 内生产。

## 从这里开始
- [规范权威与维护说明](docs/MAINTENANCE.md)
- [单工作区操作原则](docs/ops/single-workspace.md)
- [Skill准入与许可证](docs/skills/skill-policy.md)
- [三道生产关卡](docs/production-gates-v1.md)
- [视频后端契约](docs/architecture/render-backend-contract.md)
- [158秒真实试产](projects/csu-condenser-158s/README.md)

## 开发检查
```bash
python -m unittest discover -s tests -v
python scripts/validate_project.py projects/demo-smoke/project.json
```
这些测试检查结构和软件行为，**不证明**专业事实、画面质量或视频成品已经合格。

## 授权
本仓库自有代码使用根目录 `LICENSE`。第三方 Skill / 模型 / 视觉素材分别遵循其原始授权，见审查记录。 `director-storyboard` 暂缓，`anything2explainer` 仅借鉴工程方法（PolyForm Noncommercial，未整套引入）。
