param(
    [Parameter(Mandatory = $true)]
    [int]$StartBatch,

    [Parameter(Mandatory = $true)]
    [int]$MaxBatches,

    [Parameter(Mandatory = $true)]
    [string]$OutPrefix,

    [int]$AttackNum = 2,

    [int]$Average = 3,

    [int]$Interval = 10,

    [int]$K = 10,

    [string]$Dataset = 'laion5_blip',

    [string]$Scorer = 'vae_ssim',

    [string]$ScoreMode = 'first',

    [string]$OutputDir = 'chunk_outputs',

    [string]$RunName = 'rediffuse_auc_boost_blip_a2_vae'
)

$ErrorActionPreference = 'Stop'

$root = 'E:\stable_diffusion\coco_data\SD_MIA_Reproduction'
if ([System.IO.Path]::IsPathRooted($RunName)) {
    $runDir = $RunName
} else {
    $runDir = Join-Path 'E:\stable_diffusion\coco_data\runs' $RunName
}
if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    $outDir = $OutputDir
} else {
    $outDir = Join-Path $root $OutputDir
}
$py = 'C:\Users\33166\miniconda3\envs\ddim_repro\python.exe'

New-Item -ItemType Directory -Force -Path $outDir | Out-Null
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$env:HF_HUB_OFFLINE = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:SD_MIA_DATA_DIR = 'E:\stable_diffusion\coco_data\stable_diffusion_data'
$env:SD_MIA_COCO_IMG_DIR = 'E:\stable_diffusion\coco_data\coco_data\val2017'
$env:SD_MIA_COCO_ANN_FILE = 'E:\stable_diffusion\coco_data\coco_data\annotations\captions_val2017.json'
$env:SD_MIA_COCO_SPLIT_YAML = 'E:\stable_diffusion\coco_data\SD_MIA_Reproduction\coco-2500-random.yaml'

Push-Location $root
try {
    $oldErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & $py -u 'E:\stable_diffusion\coco_data\SD_MIA_Reproduction\attack.py' `
        --attacker_name ReDiffuse `
        --dataset $Dataset `
        --checkpoint CompVis/stable-diffusion-v1-4 `
        --attack_num $AttackNum `
        --interval $Interval `
        --k $K `
        --average $Average `
        --seed 0 `
        --batch_size 1 `
        --result_csv (Join-Path $runDir 'result.csv') `
        --torch_dtype auto `
        --score_mode $ScoreMode `
        --rediffuse_scorer $Scorer `
        --scores_npz (Join-Path $outDir "$OutPrefix.npz") `
        --max_batches $MaxBatches `
        --start_batch $StartBatch `
        --checkpoint_every 0 `
        --resume False 2>&1
    $ErrorActionPreference = $oldErrorActionPreference

    $lines = @($output | ForEach-Object { $_.ToString() })
    $base64 = ($lines | Where-Object { $_ -match '^[A-Za-z0-9+/=]+$' } | Select-Object -Last 1)
    $err = ($lines | Where-Object { $_ -notmatch '^[A-Za-z0-9+/=]+$' })

    $b64Path = Join-Path $outDir "$OutPrefix.b64"
    $errPath = Join-Path $outDir "$OutPrefix.err"
    $npzPath = Join-Path $outDir "$OutPrefix.npz"

    if (-not $base64) {
        Set-Content -Path $errPath -Value $err
        throw "No base64 payload found in attack output. See $errPath"
    }

    Set-Content -Path $b64Path -Value $base64
    if ($err.Count -gt 0) {
        Set-Content -Path $errPath -Value $err
    } else {
        Set-Content -Path $errPath -Value ''
    }
    [IO.File]::WriteAllBytes($npzPath, [Convert]::FromBase64String($base64))

    Write-Host "chunk_saved=$OutPrefix start=$StartBatch max=$MaxBatches npz=$npzPath"
}
finally {
    Pop-Location
}
