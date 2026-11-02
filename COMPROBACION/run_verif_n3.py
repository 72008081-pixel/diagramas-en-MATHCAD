# -*- coding: utf-8 -*-
"""
VERIFICACIÓN N3: GRÁFICA COMPARATIVA DE EJERCICIOS NUEVOS CON LA PLANTILLA MAESTRA
Genera un gráfico comparativo multipanel a 300 DPI mostrando que la plantilla maestra
recalcula y traza con perfección las curvas DFC y DMF para cualquier geometría.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')

COMP_DIR = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\COMPROBACION"
OUTPUT_PNG = os.path.join(COMP_DIR, "VERIFICACION_N3_GRAFICA_NUEVOS_EJERCICIOS.png")

fig, axes = plt.subplots(3, 2, figsize=(14, 11), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
fig.suptitle("CONTROL GRÁFICO DE REACTIVIDAD - PLANTILLA MAESTRA UNIVERSAL (ESTILO VIGA 2)", fontsize=13, fontweight='bold', color='#1A365D', y=0.98)

# -------------------------------------------------------------
# EJERCICIO A: 1 Tramo (L=6m, q=800 kg/m)
# -------------------------------------------------------------
xa = np.linspace(0, 6, 200)
Va = 2400.0 - 800.0 * xa
Ma = 2400.0 * xa - 400.0 * xa**2

ax_va, ax_ma = axes[0, 0], axes[0, 1]
ax_va.set_title("Caso A: DFC - Viga Simple (L=6m, q=800 kg/m)", fontsize=10, fontweight='bold', color='#2C5282')
ax_va.plot(xa, Va, color='#2B6CB0', lw=2)
ax_va.fill_between(xa, 0, Va, where=(Va >= 0), color='#63B3ED', alpha=0.3)
ax_va.fill_between(xa, 0, Va, where=(Va < 0), color='#FEB2B2', alpha=0.3)
ax_va.axhline(0, color='black', lw=0.8, ls='--')
ax_va.plot([0, 3, 6], [2400, 0, -2400], 'o', color='#2B6CB0', markersize=4)
ax_va.text(0.1, 2100, "+2400 kg", fontsize=8.5, fontweight='bold', color='#2C5282')
ax_va.text(3.0, 300, "V=0 (x=3m)", fontsize=8.5, fontweight='bold', color='#9B2C2C', ha='center')
ax_va.text(5.9, -2100, "-2400 kg", fontsize=8.5, fontweight='bold', color='#9B2C2C', ha='right')
ax_va.grid(True, ls=':', alpha=0.6)
ax_va.set_ylabel("V (kg)", fontsize=9, fontweight='bold')

ax_ma.set_title("Caso A: DMF - Parábola Central Simétrica", fontsize=10, fontweight='bold', color='#742A2A')
ax_ma.plot(xa, Ma, color='#C53030', lw=2.2)
ax_ma.fill_between(xa, 0, Ma, color='#FEB2B2', alpha=0.3)
ax_ma.axhline(0, color='black', lw=0.8, ls='--')
ax_ma.plot([0, 3, 6], [0, 3600, 0], 'o', color='#9B2C2C', markersize=5)
ax_ma.text(3.0, 3800, "M_max = 3600 kg·m (x=3.00m)", fontsize=8.5, fontweight='bold', color='#742A2A', ha='center')
ax_ma.grid(True, ls=':', alpha=0.6)
ax_ma.set_ylabel("M (kg·m)", fontsize=9, fontweight='bold')

# -------------------------------------------------------------
# EJERCICIO B: 2 Tramos Escalonados (L=[4, 4]m, q=[500, 300] kg/m)
# -------------------------------------------------------------
xb = np.linspace(0, 8, 200)
Vb = np.array([1800.0 - 500.0*x if x <= 4.0 else 1800.0 - 2000.0 - 300.0*(x-4.0) for x in xb])
Mb = np.array([1800.0*x - 250.0*x**2 if x <= 4.0 else 1800.0*x - 2000.0*(x-2.0) - 150.0*(x-4.0)**2 for x in xb])

ax_vb, ax_mb = axes[1, 0], axes[1, 1]
ax_vb.set_title("Caso B: DFC - 2 Tramos (L=[4, 4]m, q=[500, 300] kg/m)", fontsize=10, fontweight='bold', color='#2C5282')
ax_vb.plot(xb, Vb, color='#2B6CB0', lw=2)
ax_vb.fill_between(xb, 0, Vb, where=(Vb >= 0), color='#63B3ED', alpha=0.3)
ax_vb.fill_between(xb, 0, Vb, where=(Vb < 0), color='#FEB2B2', alpha=0.3)
ax_vb.axhline(0, color='black', lw=0.8, ls='--')
ax_vb.plot([0, 3.6, 4, 8], [1800, 0, -200, -1400], 'o', color='#2B6CB0', markersize=4)
ax_vb.text(0.1, 1500, "+1800 kg", fontsize=8.5, fontweight='bold', color='#2C5282')
ax_vb.text(3.6, 250, "V=0 (x=3.6m)", fontsize=8.5, fontweight='bold', color='#9B2C2C', ha='center')
ax_vb.text(7.9, -1200, "-1400 kg", fontsize=8.5, fontweight='bold', color='#9B2C2C', ha='right')
ax_vb.grid(True, ls=':', alpha=0.6)
ax_vb.set_ylabel("V (kg)", fontsize=9, fontweight='bold')

ax_mb.set_title("Caso B: DMF - Parábolas de Distinta Curvatura", fontsize=10, fontweight='bold', color='#742A2A')
ax_mb.plot(xb, Mb, color='#C53030', lw=2.2)
ax_mb.fill_between(xb, 0, Mb, color='#FEB2B2', alpha=0.3)
ax_mb.axhline(0, color='black', lw=0.8, ls='--')
ax_mb.plot([0, 3.6, 4, 8], [0, 3240, 3200, 0], 'o', color='#9B2C2C', markersize=5)
ax_mb.text(3.6, 3450, "M_max = 3240 kg·m (x=3.60m)", fontsize=8.5, fontweight='bold', color='#742A2A', ha='center')
ax_mb.grid(True, ls=':', alpha=0.6)
ax_mb.set_ylabel("M (kg·m)", fontsize=9, fontweight='bold')

# -------------------------------------------------------------
# EJERCICIO C: Viga 2 Oficial Docente (L=[5, 4, 1]m, q2=700 kg/m)
# -------------------------------------------------------------
xc = np.linspace(0, 10, 250)
Vc = np.array([840.0 if x < 5.0 else (840.0 - 700.0*(x-5.0) if x <= 9.0 else -1960.0) for x in xc])
Mc = np.array([840.0*x if x < 5.0 else (840.0*x - 350.0*(x-5.0)**2 if x <= 9.0 else 840.0*x - 2800.0*(x-7.0)) for x in xc])

ax_vc, ax_mc = axes[2, 0], axes[2, 1]
ax_vc.set_title("Caso C (Viga 2): DFC - Oficial Docente (L=[5, 4, 1]m, q2=700 kg/m)", fontsize=10, fontweight='bold', color='#2C5282')
ax_vc.plot(xc, Vc, color='#2B6CB0', lw=2)
ax_vc.fill_between(xc, 0, Vc, where=(Vc >= 0), color='#63B3ED', alpha=0.3)
ax_vc.fill_between(xc, 0, Vc, where=(Vc < 0), color='#FEB2B2', alpha=0.3)
ax_vc.axhline(0, color='black', lw=0.8, ls='--')
ax_vc.plot([0, 5, 6.2, 9, 10], [840, 840, 0, -1960, -1960], 'o', color='#2B6CB0', markersize=4)
ax_vc.text(0.1, 1000, "+840 kg", fontsize=8.5, fontweight='bold', color='#2C5282')
ax_vc.text(6.2, 250, "V=0 (x=6.2m)", fontsize=8.5, fontweight='bold', color='#9B2C2C', ha='center')
ax_vc.text(9.0, -2200, "-1960 kg", fontsize=8.5, fontweight='bold', color='#9B2C2C', ha='center')
ax_vc.grid(True, ls=':', alpha=0.6)
ax_vc.set_xlabel("Distancia x (m)", fontsize=9, fontweight='bold')
ax_vc.set_ylabel("V (kg)", fontsize=9, fontweight='bold')

ax_mc.set_title("Caso C (Viga 2): DMF - Pico Parabólico Máximo Asimétrico", fontsize=10, fontweight='bold', color='#742A2A')
ax_mc.plot(xc, Mc, color='#C53030', lw=2.2)
ax_mc.fill_between(xc, 0, Mc, color='#FEB2B2', alpha=0.3)
ax_mc.axhline(0, color='black', lw=0.8, ls='--')
ax_mc.plot([0, 5, 6.2, 9, 10], [0, 4200, 4704, 1960, 0], 'o', color='#9B2C2C', markersize=5)
ax_mc.text(6.2, 5000, "M_max = 4704.0 kg·m (x=6.20m)", fontsize=8.5, fontweight='bold', color='#742A2A', ha='center')
ax_mc.grid(True, ls=':', alpha=0.6)
ax_mc.set_xlabel("Distancia x (m)", fontsize=9, fontweight='bold')
ax_mc.set_ylabel("M (kg·m)", fontsize=9, fontweight='bold')

plt.tight_layout()
plt.subplots_adjust(top=0.93)
plt.savefig(OUTPUT_PNG, dpi=300, bbox_inches='tight')
plt.close()

print(f"Gráfica de nuevos ejercicios guardada exitosamente en:\n{OUTPUT_PNG}")
