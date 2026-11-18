$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromePath) {
    Start-Process $chromePath -ArgumentList "http://localhost:5173/ --new-tab"
} else {
    Start-Process "http://localhost:5173/"
}
Start-Sleep -Milliseconds 800
$wshell = New-Object -ComObject WScript.Shell
$wshell.AppActivate("Google Chrome")
$wshell.AppActivate("OceanEmbed")
Write-Output "Chrome launched and focused"
