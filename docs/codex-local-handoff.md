# 单目录生产：Windows / macOS

最新视觉关卡：读取docs/decisions/2026-10-12-film-visual-route.md。下面旧图预览命令只描述上一轮验证方法，现在执行会被阻止；最新用户V1已授权并产出首批SH003、SH008–SH011，SH007原图复用；依据docs/production/keyframes-v1/验收首批，再决定剩余20镜。不把旧工程草图用于新动画。

当前集成尚未合并；按本轮 PR 的施工分支检出，不假定 main 已含流水线。

采用最新cloud-neutral决策，不固定T470s、F117或M4为主控。已有机器可运行本轮确定性脚本和图层预览，无需专用GPU；未来按质量、时间和实际总成本比较托管云端与本地方案，不自动付费或搭建常驻模型服务。

Windows PowerShell（在仓库根目录）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_pilot.ps1
# 可选：固定上游源检出，并将 MIT storyboard 技能安装到本项目的发现目录
powershell -ExecutionPolicy Bypass -File .\scripts\setup_pilot.ps1 -WithUpstreams -InstallStoryboard
py -3 scripts/import_csu.py 'C:\实际路径\第3组_凝汽器与真空系统_158秒AI科普分镜脚本.xlsx'
py -3 -m unittest discover -s tests -v
py -3 scripts/validate_pilot.py
py -3 scripts/render_keyframes.py --png
py -3 scripts/clip_runner.py --shot SH009
# 仅供审核的草稿预览，无收费服务
py -3 scripts/clip_runner.py --shot SH009 --execute --preview
```

macOS/Linux：将 `py -3` 换成 `python3`，初始化用 `python3 scripts/setup_pilot.py`；可选 `--with-upstreams --install-storyboard`。所有 Python 路径以脚本所在仓库为根；导入器默认输出相对当前目录，因此导入时仍在仓库根目录运行，或明确传 `--out`。

Python 3.10+。导入、校验、安装、SVG渲染仅用标准库与 Git。PNG渲染需 Pillow，预览需 Pillow+FFmpeg/ffprobe（编码器 libx264）；未安装时只提供 SVG 和 dry-run。不得自动下载模型。此环境实测 Pillow+FFmpeg 已有，具体用户设备需 `clip_runner.py --probe`。

六岗位在 `.agents/skills/<role>/SKILL.md`，符合项目技能发现布局；Work 已逐一读过，doctor 检查入口。未在用户桌面 Codex 实际启动任务，新增加技能后可重启已有会话。可选 MIT 技能复制完整技能目录，附 LICENSE 和版本/文件哈希；安装目录被 Git 忽略。director-storyboard已被最新决策暂停，不克隆、安装或执行；注册中的版本仅作归档。

原始 Excel、上游克隆、安装副本、PNG、片段、临时运行记录和人工批准文件均忽略，不推入公开仓库。candidate.json/md、任务包与原创 master.svg 是可审查生产规格。

## 最小 Codex 指令

读取 AGENTS.md，然后按一个岗位一次执行。先检查 `python scripts/validate_pilot.py` 和六技能 doctor，不重新生成已存在规格。读取 candidate.md、script-review.md、master-spec.json 与 visual-review.md；先交专业审阅者确认草稿，不擅自签署 APPROVED。获批前只可执行本地 SVG/PNG草稿和 `clip_runner.py --execute --preview`；禁止收费调用与模型下载。默认续做 SH003、SH007–SH011，先复用已生成哈希匹配的素材。审批后生产命令必须使用匹配哈希的批准文件。若仍是 REVIEW，汇报具体未批准项。不要改题材，不启动六个 Agent，不制作骨架 UI。

## 人工批准记录

在被忽略的 `projects/csu-condenser-158s/reviews/approval.json` 中记录下面字段。占位字段不能运行生产；专业审阅者必须看过本次文本、母版及每张首尾图后填真实信息。

```json
{
  "status": "APPROVED",
  "reviewer": "真实专业审阅者姓名",
  "reviewed_at": "真实ISO8601时间",
  "script_sha256": "candidate.json的实际SHA256",
  "master_sha256": "master-spec.json的实际SHA256",
  "frames": {"SH009": {"start": "实际PNG哈希", "end": "实际PNG哈希"}}
}
```

生产示例：`python scripts/clip_runner.py --shot SH009 --execute --approval projects/csu-condenser-158s/reviews/approval.json`。生产完成仍只表示编码成功，片段还需检查。
