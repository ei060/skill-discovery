# AWS VPS SSH 连接 (PowerShell)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AWS VPS SSH 连接" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "连接到: aws-uqiha (3.86.220.54)" -ForegroundColor Green
Write-Host "用户: ubuntu" -ForegroundColor Green
Write-Host ""

$sshKey = "C:\Users\DELL\.ssh\uqiha1.pem"
$host = "ubuntu@3.86.220.54"

# 检查密钥文件是否存在
if (Test-Path $sshKey) {
    # 使用 SSH 连接
    ssh -i $sshKey $host
} else {
    Write-Host "[ERROR] 密钥文件不存在: $sshKey" -ForegroundColor Red
}

Write-Host ""
Write-Host "连接已关闭" -ForegroundColor Yellow
Read-Host "按回车键退出"
