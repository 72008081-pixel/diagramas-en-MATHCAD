import subprocess, glob, os, sys

sys.stdout.reconfigure(encoding='utf-8')

log_dir = r"C:\ProgramData\PTC\Mathcad Prime\Logs"
base_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD"

subprocess.run(["powershell", "-Command", "Stop-Process -Name 'MathcadPrime' -Force -ErrorAction SilentlyContinue"], capture_output=True)

test_files = [
    os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx"),
    os.path.join(base_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"),
    os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx"),
    os.path.join(base_dir, "EJERCICIO-01.mcdx"),
    os.path.join(base_dir, "COMPROBACION", "PLANTILLA_MAESTRA_DESDE_CERO_ESTILO_PROFESOR.mcdx")
]

all_passed = True
for fpath in test_files:
    fname = os.path.basename(fpath)
    before_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))
    
    ps_cmd = f"""
    $app = New-Object -ComObject MathcadPrime.Application
    $app.Visible = $false
    try {{
        $app.Open("{fpath}")
        Start-Sleep -Milliseconds 600
        $c = $app.Worksheets.Count
        Write-Host "OPENED count: $c"
    }} catch {{
        Write-Host "ERR: $($_.Exception.Message)"
    }} finally {{
        $app.CloseAll(2)
        $app.Quit(2)
    }}
    """
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, timeout=25)
    after_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))
    new_logs = after_logs - before_logs
    
    if len(new_logs) == 0 and "OPENED count" in res.stdout:
        print(f"✅ PASSED (0 Exceptions): {fname}")
    else:
        print(f"❌ FAILED: {fname}")
        for l in new_logs:
            print("   Log:", l)
            with open(l, 'r', encoding='utf-8', errors='ignore') as logf:
                for line in logf.readlines()[10:25]:
                    print("     ", line.strip())
        all_passed = False

if all_passed:
    print("\n🎉 ALL MASTER TEMPLATES OPENED 100% CLEANLY IN MATHCAD PRIME 11!")
