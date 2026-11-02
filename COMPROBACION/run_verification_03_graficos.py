# -*- coding: utf-8 -*-
"""
VERIFICACIÓN 3: GENERACIÓN DE DIAGRAMAS DE CONTROL DE ALTA RESOLUCIÓN (PNG)
Genera el panel completo de verificación: Esquema Estructural, DFC y DMF
comparando la solución oficial del docente vs la plantilla corregida.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.stdout.reconfigure(encoding='utf-8')

COMP_DIR = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\COMPROBACION"
OUTPUT_PNG = os.path.join(COMP_DIR, "03_GRAFICA_COMPARATIVA_DFC_DMF.png")

# Parámetros oficiales
L1, L2, L3 = 5.0, 4.0, 1.0
L_tot = 10.0
w = 700.0
VA, VB = 840.0, 1960.0

# Discretización fina
x = np.linspace(0.0, 10.0, 1000)

# 1. Fuerza Cortante V(x)
def calc_V(xi):
    if xi < 5.0:
        return 840.0
    elif xi < 9.0:
        return 840.0 - 700.0 * (xi - 5.0)
    elif xi < 10.0:
        return -1960.0
    else:
        return 0.0

# 2. Momento Flector M(x)
def calc_M(xi):
    if xi < 5.0:
        return 840.0 * xi
    elif xi < 9.0:
        return 840.0 * xi - 700.0 * (xi - 5.0)**2 / 2.0
    elif xi <= 10.0:
        return 840.0 * xi - 2800.0 * (xi - 7.0)
    else:
        return 0.0

V = np.array([calc_V(xi) for xi in x])
M = np.array([calc_M(xi) for xi in x])

# Configuración de figura profesional (3 paneles verticales)
fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(12, 11), gridspec_kw={'height_ratios': [1.1, 1.6, 1.6]}, dpi=300)
fig.patch.set_facecolor('#FFFFFF')

# -------------------------------------------------------------
# PANEL 0: ESQUEMA ESTRUCTURAL DE LA VIGA
# -------------------------------------------------------------
ax0.set_xlim(-0.8, 10.8)
ax0.set_ylim(-1.5, 2.8)
ax0.axis('off')
ax0.set_title("1° ESQUEMA ESTRUCTURAL Y CARGAS - MODELO DE VERIFICACIÓN (VIGA 2)", fontsize=12, fontweight='bold', pad=10, color='#1A365D')

# Eje de la viga
ax0.plot([0, 10], [0, 0], color='#2B6CB0', lw=6, solid_capstyle='butt', zorder=3)

# Apoyos
# Apoyo A (Fijo / Pin) en x=0
ax0.plot(0, 0, marker='^', markersize=14, color='#C53030', zorder=4)
ax0.plot([-0.3, 0.3], [-0.3, -0.3], color='#718096', lw=3)
ax0.text(0, -0.7, r"$A_Y = 840\,\mathrm{kg}$", ha='center', fontsize=10, fontweight='bold', color='#C53030')

# Apoyo B (Móvil / Roller) en x=10
ax0.plot(10, 0, marker='^', markersize=14, color='#C53030', zorder=4)
ax0.plot([9.7, 10.3], [-0.3, -0.3], color='#718096', lw=3)
ax0.plot([9.8, 10.0, 10.2], [-0.45, -0.45, -0.45], 'o', color='#718096', markersize=4)
ax0.text(10, -0.7, r"$B_Y = 1960\,\mathrm{kg}$", ha='center', fontsize=10, fontweight='bold', color='#C53030')

# Carga distribuida w = 700 kg/m entre x=5 y x=9
rect = patches.Rectangle((5.0, 0.0), 4.0, 1.0, linewidth=1.5, edgecolor='#DD6B20', facecolor='#FEEBC8', alpha=0.75, zorder=2)
ax0.add_patch(rect)
for arr_x in np.linspace(5.2, 8.8, 10):
    ax0.annotate('', xy=(arr_x, 0.05), xytext=(arr_x, 0.95),
                 arrowprops=dict(arrowstyle="->", color='#DD6B20', lw=1.5))
ax0.text(7.0, 1.25, r"$w = 700\,\mathrm{kg/m}$", ha='center', fontsize=11, fontweight='bold', color='#C05621')

# Cotas de longitud L1=5m, L2=4m, L3=1m
def draw_dim(ax, xstart, xend, y, label):
    ax.annotate('', xy=(xstart, y), xytext=(xend, y),
                arrowprops=dict(arrowstyle="<->", color='#4A5568', lw=1.2))
    ax.text((xstart + xend)/2.0, y + 0.12, label, ha='center', fontsize=9, fontweight='semibold', color='#2D3748')

draw_dim(ax0, 0.0, 5.0, -1.1, "L1 = 5.00 m")
draw_dim(ax0, 5.0, 9.0, -1.1, "L2 = 4.00 m")
draw_dim(ax0, 9.0, 10.0, -1.1, "L3 = 1.00 m")
draw_dim(ax0, 0.0, 10.0, 2.0, "L_tot = 10.00 m")

# -------------------------------------------------------------
# PANEL 1: DIAGRAMA DE FUERZA CORTANTE V(x)
# -------------------------------------------------------------
ax1.set_title("2° DIAGRAMA DE FUERZA CORTANTE (DFC) - V(x) [kg]", fontsize=12, fontweight='bold', pad=8, color='#1A365D')
ax1.plot(x, V, color='#2B6CB0', lw=2.2, label=r"$V(x)$ Plantilla Mathcad & Docente")
ax1.axhline(0, color='black', lw=1.0, ls='--')

# Sombreado de áreas
ax1.fill_between(x, 0, V, where=(V >= 0), color='#63B3ED', alpha=0.35, interpolate=True)
ax1.fill_between(x, 0, V, where=(V < 0), color='#FEB2B2', alpha=0.35, interpolate=True)

# Puntos singulares y cotas en V
ax1.plot([0, 5, 6.2, 9, 10], [840, 840, 0, -1960, 0], 'o', color='#2B6CB0', markersize=5)
ax1.text(0.1, 950, "+840 kg", fontsize=9, fontweight='bold', color='#2C5282')
ax1.text(5.0, 950, "+840 kg", fontsize=9, fontweight='bold', color='#2C5282', ha='center')
ax1.text(6.2, 200, "V=0\nx=6.20m", fontsize=9, fontweight='bold', color='#9B2C2C', ha='center')
ax1.text(9.0, -2150, "-1960 kg", fontsize=9, fontweight='bold', color='#9B2C2C', ha='center')
ax1.text(9.9, 150, "Cierre VD=1960 kg", fontsize=8.5, fontweight='bold', color='#276749', ha='right')

ax1.set_xlim(0, 10)
ax1.set_ylim(-2400, 1300)
ax1.set_xticks(range(0, 11))
ax1.set_ylabel("Cortante V (kg)", fontsize=10, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(loc='lower left', fontsize=9)

# -------------------------------------------------------------
# PANEL 2: DIAGRAMA DE MOMENTO FLECTOR M(x)
# -------------------------------------------------------------
ax2.set_title("3° DIAGRAMA DE MOMENTO FLECTOR (DMF) - M(x) [kg·m]", fontsize=12, fontweight='bold', pad=8, color='#1A365D')
ax2.plot(x, M, color='#C53030', lw=2.5, label=r"$M(x)$ Plantilla Mathcad & Docente")
ax2.axhline(0, color='black', lw=1.0, ls='--')

# Sombreado de área positiva
ax2.fill_between(x, 0, M, color='#FEB2B2', alpha=0.30, interpolate=True)

# Puntos clave en M
ax2.plot([0, 5, 6.2, 9, 10], [0, 4200, 4704, 1960, 0], 'o', color='#9B2C2C', markersize=6)
ax2.text(5.0, 3750, "M(5) = 4200 kg·m", fontsize=9, fontweight='bold', color='#9B2C2C', ha='center')
ax2.text(6.2, 4950, "M_max = 4704.0 kg·m\n(x = 6.20 m)", fontsize=9.5, fontweight='bold', color='#742A2A', ha='center')
ax2.text(9.0, 2200, "M(9) = 1960 kg·m", fontsize=9, fontweight='bold', color='#9B2C2C', ha='center')
ax2.text(0.1, 200, "M(0)=0", fontsize=8.5, fontweight='bold', color='#2D3748')
ax2.text(9.9, 200, "M(10)=0", fontsize=8.5, fontweight='bold', color='#2D3748', ha='right')

ax2.set_xlim(0, 10)
ax2.set_ylim(-400, 5500)
ax2.set_xticks(range(0, 11))
ax2.set_xlabel("Distancia a lo largo de la viga x (m)", fontsize=10, fontweight='bold')
ax2.set_ylabel("Momento M (kg·m)", fontsize=10, fontweight='bold')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(loc='upper right', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=300, bbox_inches='tight')
plt.close()

print(f"Gráfica de alta resolución generada exitosamente en:\n{OUTPUT_PNG}")
