param(
    [Parameter(Mandatory = $true)]
    [int]$WaitPid,

    [Parameter(Mandatory = $true)]
    [string]$AssetsRoot,

    [string]$RunSuffix = "strong-v2",
    [int]$Epochs = 3,
    [int]$SigmaNoiseSamples = 2,
    [int]$BasePort = 6040
)

$ErrorActionPreference = "Stop"

while (Get-Process -Id $WaitPid -ErrorAction SilentlyContinue) {
    Start-Sleep -Seconds 15
}

powershell -ExecutionPolicy Bypass -File "D:\Code\DiffAudit\Project\scripts\launch_dpdm_shadow_sequence.ps1" `
    -AssetsRoot $AssetsRoot `
    -RunSuffix $RunSuffix `
    -Epochs $Epochs `
    -SigmaNoiseSamples $SigmaNoiseSamples `
    -BasePort $BasePort
