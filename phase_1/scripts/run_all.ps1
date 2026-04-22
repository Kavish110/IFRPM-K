<#
.SYNOPSIS
    NGAFID ML Pipeline Master Script (PowerShell)
.EXAMPLE
    .\scripts\run_all.ps1 -model cnn -size_ratio 0.1 -debug true
#>

param (
    [string]$dataset = "ngafid",
    [double]$size_ratio = 0.1,
    [string]$model = "cnn",
    [string]$debug = "true",
    [string]$task = "all"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " NGAFID ML Pipeline (Windows/PowerShell)"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Model:      $model"
Write-Host " Size ratio: $size_ratio"
Write-Host " Debug:      $debug"
Write-Host " Task:       $task"
Write-Host "============================================" -ForegroundColor Cyan

python main.py --dataset $dataset --size_ratio $size_ratio --model $model --debug $debug --task $task

Write-Host "`nPipeline Execution Finished." -ForegroundColor Green
