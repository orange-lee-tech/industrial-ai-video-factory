# 唯一生产标准与维护规则 — 2026-10-12

**main 是唯一持续开发主干。** 旧试产分支不作为施工目标，已合并/替代的历史分支不再次重复合并。临时分支短期审查完毕后关闭；归档快照非活跃产线。GitHub 不承担视频存储/推理任务。

## 权威顺序
1. `docs/decisions/2026-10-12-video-capability-and-pivot.md`：**最新现实能力评估与停工边界**；与旧文件冲突时以本决策为准。
2. `00_constitution/production-principles-v1.md`：基本安全、真实性、成本原则。
3. `docs/production/keyframes-v1/`：静态关键帧规范；不再强制每镜出图。
4. `contracts/` / validators：格式和静态检查（不具备媒体美学评估能力）。
5. `docs/ops/`、`.agents/skills/`：可复用操作说明； `projects/csu-condenser-158s/`：试样记录而非通用政策。

## Skill / 许可
- create-storyboard：MIT，批准作为参考；不强制安装。
- director-storyboard：DEFERRED，不安装、不调用。
- anything2explainer：研究其方法，不包含其 PolyForm Noncommercial 工具包；直接商业使用需要授权。
- 不再为试样先扩建 Skill/常驻 GPU/远端队列。

## 现实生产状态
- 六张 PNG 为静态美术候选，专业审核独立。
- SH009–SH011 pilot01：FAIL（幻灯片感）；pilot02：FAIL（不自然素材平移）；原视频、脚本、SVG 归档，**禁止当作生产后端默认路径**。
- 26 镜/158 秒正式电影未交付；没有真实运动验收 PASS。
- 只允许下一轮小范围免费或既有权益的**自然运动生成方法**验证。收费推理必须先获明确批准。

## 操作
`python -m unittest discover -s tests -v`；静态 CI PASS 不代表动画自然或工业事实无误。任何交接必须报告：已实证通过/人类拒绝/未试验三类状态，禁止伪造批准。
