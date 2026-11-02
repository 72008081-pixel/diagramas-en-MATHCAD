# -*- coding: utf-8 -*-
import sys, os, glob, subprocess
sys.stdout.reconfigure(encoding='utf-8')

import mcdx_dynamic_builder as builder

base_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD"
template = os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx")
out_file = os.path.join(base_dir, "test_5spans_user_case.mcdx")

# Caso similar al screenshot del usuario: 5 tramos
spans = [2.0, 3.0, 2.5, 1.5, 2.0]
dist_loads = [15.0, 0.0, 20.0, 0.0, 10.0]
point_loads = [0.0, 25.0, 0.0, 30.0, 0.0, 0.0]
applied_moments = [0.0, 0.0, 15.0, 0.0, 0.0, 0.0]
sup_indices = (0, 4) # Apoyo A en x0, Apoyo B en x4

builder.generate_custom_beam_mcdx(
    template,
    out_file,
    spans=spans,
    dist_loads=dist_loads,
    point_loads=point_loads,
    applied_moments=applied_moments,
    sup_indices=sup_indices
)

print(f"Generated: {out_file}")

# Test open in Mathcad Prime 11 via COM
log_dir = r"C:\ProgramData\PTC\Mathcad Prime\Logs"
before_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))

ps_cmd = f"""
$app = New-Object -ComObject MathcadPrime.Application
$app.Visible = $false
try {{
    $ws = $app.Open("{out_file}")
    Start-Sleep -Milliseconds 800
    Write-Host "OPENED_OK Count: $($app.Worksheets.Count)"
}} catch {{
    Write-Host "ERR: $($_.Exception.Message)"
}} finally {{
    $app.CloseAll(2)
    $app.Quit(2)
}}
"""

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, timeout=30)
print("STDOUT:", res.stdout.strip())
if res.stderr: print("STDERR:", res.stderr.strip())

after_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))
new_logs = after_logs - before_logs
print("New exception logs:", len(new_logs))
if len(new_logs) == 0 and "OPENED_OK Count: 1" in res.stdout:
    print("SUCCESS: 5-span dynamic beam opened cleanly with 0 exceptions!")
else:
    print("FAILED! Logs:")
    for l in new_logs:
        print("  Log:", l)
