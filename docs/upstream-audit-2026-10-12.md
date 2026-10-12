# 固定上游审查

| 上游 | 固定提交 | 许可 | 本轮实测 |
| --- | --- | --- | --- |
| TateZhouSiu/create-storyboard-skill | 4b8662e2fee51b37488c77952bbfa302bfeaf36c | 根 LICENSE：MIT | 完整检出；脚手架158s/16:9离线执行成功；项目发现目录完整安装成功 |
| ai2764/ai-video-skills | a42f31adcd733719f1234b1ba42743af83bde086 | 未发现明确根 LICENSE | 完整检出；读取入口、共享脚本和后端契约；未执行推理、未公开复制其代码 |

create-storyboard 的 pyproject 要求 Python>=3.10、依赖为空；脚手架只用 argparse/pathlib，创建文件时默认不覆盖。它生成模板，不能代替本片填充与专业审查。本轮只吸收一镜一单元、首尾态及镜间交接方法，不重复生成大量空白 bible。

director-storyboard 的入口在 codex/director-storyboard，脚本/workflows在仓库根目录。共享代码含 urllib 到 ComfyUI、MiniMax API提交、读取环境API密钥以及FFmpeg缩略图功能；不能当作纯离线生成器。run_storyboard默认也会探测网络服务，--dry-run不等于无网络。因此本轮不执行它的 probe/run，不安装模型或调用收费端。其 pyproject只列 pytest 配置，不足以证明全部模型节点和运行依赖齐备。

setup_pilot.py 固定从 registry/approved-skills.json 读来源与SHA，检查remote、拒绝覆盖本地已跟踪编辑、检查入口及MIT许可。可选安装仅复制MIT技能完整目录到 `.agents/skills/create-storyboard`，附许可与逐文件来源哈希，目录被忽略。无许可的第二技能不会自动安装至发现目录或进入公开代码。

六个本项目岗位入口均实读并通过doctor；增补实际命令、输出路径和审批边界。自动发现的布局/元数据已检查，本环境未启动独立桌面Codex会话验证运行时列表。Linux安装实测成功；Windows/macOS原生兼容由新增CI矩阵验证，不能仅由Linux结果推出。

本仓库主分支已由用户配置 MIT License（Orange Lee, 2026），本轮保留。该许可不授予上游无许可代码、模型权重或他人素材使用权。
