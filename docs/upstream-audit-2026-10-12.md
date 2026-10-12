# 固定上游审查

| 上游 | 固定提交 | 许可 | 本轮实测 |
| --- | --- | --- | --- |
| TateZhouSiu/create-storyboard-skill | 4b8662e2fee51b37488c77952bbfa302bfeaf36c | 根 LICENSE：MIT | 完整检出；脚手架158s/16:9离线执行成功；项目发现目录完整安装成功 |
| ai2764/ai-video-skills | a42f31adcd733719f1234b1ba42743af83bde086 | 未发现明确根 LICENSE | 早期按旧授权检出并只读；后续发现新决策，已暂停并删除本轮本地副本；不安装或执行 |

create-storyboard 的 pyproject 要求 Python>=3.10、依赖为空；脚手架只用 argparse/pathlib，创建文件时默认不覆盖。它生成模板，不能代替本片填充与专业审查。本轮只吸收一镜一单元、首尾态及镜间交接方法，不重复生成大量空白 bible。

director-storyboard 的入口在 codex/director-storyboard，脚本/workflows在仓库根目录。共享代码含 urllib 到 ComfyUI、MiniMax API提交、读取环境API密钥以及FFmpeg缩略图功能；不能当作纯离线生成器。run_storyboard默认也会探测网络服务，--dry-run不等于无网络。因此本轮不执行它的 probe/run，不安装模型或调用收费端。其 pyproject只列 pytest 配置，不足以证明全部模型节点和运行依赖齐备。

setup_pilot.py 固定从 registry/approved-skills.json 读来源与SHA，检查remote、拒绝覆盖本地已跟踪编辑、检查入口及MIT许可。可选安装仅复制MIT技能完整目录到 `.agents/skills/create-storyboard`，附许可与逐文件来源哈希，目录被忽略。无许可的第二技能已设DEFERRED；初始化仅遍历明确获批的MIT条目，不能通过--with-upstreams克隆它。

六个本项目岗位入口均实读并通过doctor；增补实际命令、输出路径和审批边界。自动发现的布局/元数据已检查，本环境未启动独立桌面Codex会话验证运行时列表。Linux安装实测成功；Windows/macOS原生兼容由新增CI矩阵验证，不能仅由Linux结果推出。

本仓库主分支已由用户配置 MIT License（Orange Lee, 2026），本轮保留。该许可不授予上游无许可代码、模型权重或他人素材使用权。

提交前再次核验发现main新增d92fb87决策，PR#2更新到dbf4d20。本轮完整采纳：不再克隆/安装/运行director-storyboard，使用不固定设备的cloud-neutral策略。旧研究发生在发现这项更新之前；本轮已移除检出副本，未保留任何无许可代码在公开树。
