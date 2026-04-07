param(
    [Parameter(Mandatory = $true)]
    [string]$AssetsRoot,

    [string[]]$Shadows = @("shadow-02", "shadow-03"),
    [string]$RunSuffix = "smoke-v1",
    [string]$PythonExe = "C:\Users\Ding\miniforge3\envs\diffaudit-research\python.exe",
    [string]$DpdmRoot = "D:\Code\DiffAudit\Project\external\DPDM",
    [string]$ConfigPath = "D:\Code\DiffAudit\Project\external\DPDM\configs\cifar10_32\train_eps_10.0.yaml",
    [int]$BatchSize = 64,
    [int]$Epochs = 1,
    [int]$SigmaNoiseSamples = 1,
    [string]$DeviceBackend = "gloo",
    [int]$BasePort = 6032
)

$ErrorActionPreference = "Stop"

$writeLabelsScript = "D:\Code\DiffAudit\Project\scripts\write_imagefolder_labels.py"
$launchDpdmScript = "D:\Code\DiffAudit\Project\scripts\launch_dpdm_training.ps1"

for ($i = 0; $i -lt $Shadows.Length; $i++) {
    $shadowName = $Shadows[$i]
    $datasetDir = Join-Path $AssetsRoot "datasets\$shadowName-member"
    $workdir = "runs/dpdm-cifar10-$($shadowName.Replace('-', ''))-eps10-gpu-$RunSuffix"
    $masterPort = $BasePort + $i

    Write-Host "Preparing labels for $shadowName"
    & $PythonExe $writeLabelsScript --dataset-dir $datasetDir | Out-Host

    Write-Host "Launching DPDM $shadowName -> $workdir"
    $launchJson = powershell -ExecutionPolicy Bypass -File $launchDpdmScript `
        -DataPath $datasetDir `
        -Workdir $workdir `
        -PythonExe $PythonExe `
        -DpdmRoot $DpdmRoot `
        -ConfigPath $ConfigPath `
        -BatchSize $BatchSize `
        -Epochs $Epochs `
        -SigmaNoiseSamples $SigmaNoiseSamples `
        -DeviceBackend $DeviceBackend `
        -MasterPort $masterPort

    $launch = $launchJson | ConvertFrom-Json
    $childPid = [int]$launch.pid
    Write-Host "Spawned PID $childPid"

    while (Get-Process -Id $childPid -ErrorAction SilentlyContinue) {
        Start-Sleep -Seconds 15
    }

    Write-Host "Completed DPDM $shadowName"
}
