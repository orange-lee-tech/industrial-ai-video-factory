param([string]$Root = (Split-Path $PSScriptRoot -Parent), [switch]$WithUpstreams, [switch]$InstallStoryboard)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path $Root).Path
$launcher = $null
$prefix = @()
if (Get-Command py -ErrorAction SilentlyContinue) { $launcher = 'py'; $prefix = @('-3') }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $launcher = 'python' }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $launcher = 'python3' }
else { throw 'Python 3.10+ missing' }
$argsList = $prefix + @((Join-Path $PSScriptRoot 'setup_pilot.py'), '--root', $Root)
if ($WithUpstreams) { $argsList += '--with-upstreams' }
if ($InstallStoryboard) { $argsList += '--install-storyboard' }
& $launcher @argsList
if ($LASTEXITCODE -ne 0) { throw 'Pilot setup failed; see preceding error' }
