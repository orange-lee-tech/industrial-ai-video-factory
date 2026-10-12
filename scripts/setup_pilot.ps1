param([string]$Root = (Resolve-Path ".").Path, [switch]$WithUpstreams)
$ErrorActionPreference = "Stop"
Set-Location $Root
$project = Join-Path $Root "projects/csu-condenser-158s"
@("source","script","keyframes","clips","reviews","exports","references","tmp") | ForEach-Object { New-Item -ItemType Directory -Force -Path (Join-Path $project $_) | Out-Null }
Write-Host "Pilot directories ready: $project"
if ($WithUpstreams) {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git missing" }
  $up = Join-Path $Root ".upstreams"; New-Item -ItemType Directory -Force -Path $up | Out-Null
  $entries = @(@("create-storyboard-skill","https://github.com/TateZhouSiu/create-storyboard-skill.git","4b8662e2fee51b37488c77952bbfa302bfeaf36c"),@("ai-video-skills","https://github.com/ai2764/ai-video-skills.git","a42f31adcd733719f1234b1ba42743af83bde086"))
  foreach($e in $entries){
    $dest=Join-Path $up $e[0]
    if(-not (Test-Path $dest)){ git clone --no-checkout $e[1] $dest; if($LASTEXITCODE -ne 0){throw "clone failed: $($e[0])"} }
    git -C $dest fetch --depth 1 origin $e[2]; if($LASTEXITCODE -ne 0){throw "fetch failed: $($e[0])"}
    git -C $dest checkout --detach $e[2]; if($LASTEXITCODE -ne 0){throw "checkout failed: $($e[0])"}
    $sha = (git -C $dest rev-parse HEAD).Trim(); if($sha -ne $e[2]){throw "revision mismatch"}
    Write-Host "Pinned upstream: $($e[0])@$sha"
  }
  Write-Host "Upstream skills are source-available at .upstreams; no code executed or API invoked."
  Write-Host "Codex can read .upstreams/ai-video-skills/codex/director-storyboard/SKILL.md with its shared scripts, and .upstreams/create-storyboard-skill/skills/create-storyboard/SKILL.md."
}
Write-Host "Next: python scripts/import_csu.py 'path-to-original.xlsx' "
