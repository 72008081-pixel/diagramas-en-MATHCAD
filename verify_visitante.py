import subprocess, glob, os

mcdx_path = r"D:\Visitante\Documents\PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"
log_dir = r"C:\ProgramData\PTC\Mathcad Prime\Logs"
before_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))

ps_script = f"""
$app = New-Object -ComObject MathcadPrime.Application
$app.Visible = $false
try {{
    $path = "{mcdx_path}"
    $app.Open($path)
    Start-Sleep -Milliseconds 1000
    Write-Host "OPENED_OK: $($app.ActiveWorksheet.Title)"
}} catch {{
    Write-Host "ERR: $($_.Exception.Message)"
}} finally {{
    $app.CloseAll(2)
    $app.Quit(2)
}}
"""

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script], capture_output=True, text=True, timeout=30)
print("STDOUT:", res.stdout.strip())
after_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))
new_logs = after_logs - before_logs
print("New exception logs count:", len(new_logs))
if len(new_logs) == 0:
    print("✅ CONFIRMED: 0 EXCEPTIONS LOGGED FOR VISITANTE DOCUMENTS FILE!")
