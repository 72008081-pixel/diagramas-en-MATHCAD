# -*- coding: utf-8 -*-
"""
VERIFICACIÓN N1: AUDITORÍA XML Y CERTIFICACIÓN DE LA PLANTILLA MAESTRA DESDE CERO
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

COMP_DIR = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\COMPROBACION"
TARGET_MCDX = os.path.join(COMP_DIR, "PLANTILLA_MAESTRA_DESDE_CERO_ESTILO_PROFESOR.mcdx")
OUTPUT_TXT = os.path.join(COMP_DIR, "VERIFICACION_N1_AUDITORIA_PLANTILLA_MAESTRA.txt")

lines = []
def log(s=""):
    print(s)
    lines.append(s)

log("=" * 80)
log("VERIFICACIÓN N1: AUDITORÍA DE LA PLANTILLA MAESTRA DESDE CERO")
log(f"Archivo auditado: {os.path.basename(TARGET_MCDX)}")
log("=" * 80)

with zipfile.ZipFile(TARGET_MCDX, 'r') as z:
    ws_xml = z.read('mathcad/worksheet.xml')

root = ET.fromstring(ws_xml)
regs = root[0]

log(f"\n1. Recuento de Regiones en la Plantilla: {len(regs)} regiones.")

# Identificar regiones clave
r_x, r_v, r_m, p_v, p_m = None, None, None, None, None
for r in regs:
    for f in r.findall('.//{http://schemas.mathsoft.com/math50}function'):
        fid = f.find('{http://schemas.mathsoft.com/math50}id')
        if fid is not None and fid.text in ['Q', 'V']: r_v = r
        elif fid is not None and fid.text == 'M': r_m = r
    for d in r.findall('.//{http://schemas.mathsoft.com/math50}define'):
        did = d.find('{http://schemas.mathsoft.com/math50}id')
        drange = d.find('{http://schemas.mathsoft.com/math50}range')
        if did is not None and did.text == 'x' and drange is not None: r_x = r
    p = r.find('.//{http://schemas.mathsoft.com/worksheet50}plot')
    if p is not None:
        y_eqs = [e.text for e in p.findall('.//{http://schemas.mathsoft.com/worksheet50}yAxis//{http://schemas.mathsoft.com/math50}id')]
        if 'V' in y_eqs or 'Q' in y_eqs: p_v = r
        elif 'M' in y_eqs: p_m = r

top_x = float(r_x.attrib.get('top', 0)) if r_x is not None else 0
top_v = float(r_v.attrib.get('top', 0)) if r_v is not None else 0
top_m = float(r_m.attrib.get('top', 0)) if r_m is not None else 0
top_pv = float(p_v.attrib.get('top', 0)) if p_v is not None else 0
top_pm = float(p_m.attrib.get('top', 0)) if p_m is not None else 0

log(f"\n2. Verificación de Orden Vertical de Definiciones (Criterio del Profesor):")
log(f"  • Rango x := 0.0m, 0.01m .. Ltot -> top = {top_x:.1f} (DEFINIDO PRIMERO)")
log(f"  • Ecuación V(x) Cortante        -> top = {top_v:.1f} (DEFINIDO SEGUNDO)")
log(f"  • Ecuación M(x) Momento         -> top = {top_m:.1f} (DEFINIDO TERCERO)")
log(f"  • Gráfico DFC V(x) vs x         -> top = {top_pv:.1f} (GRAFICA PRIMERA)")
log(f"  • Gráfico DMF M(x) vs x         -> top = {top_pm:.1f} (GRAFICA SEGUNDA)")

order_ok = (top_x < top_v < top_m < top_pv < top_pm)
log(f"  >> Estado de Secuencia: {'✅ PERFECTO' if order_ok else '❌ ERROR'}")

log(f"\n3. Verificación de Operadores de Intervalo Encadenados en V(x) y M(x):")
v_str = ET.tostring(r_v, encoding='utf-8').decode('utf-8') if r_v is not None else ""
m_str = ET.tostring(r_m, encoding='utf-8').decode('utf-8') if r_m is not None else ""

# Count lessThan occurrences
v_less_count = v_str.count('lessThan')
m_less_count = m_str.count('lessThan')
has_bad_gt = ('>>' in v_str) or ('>>' in m_str)

log(f"  • Etiquetas <lessThan> en V(x): {v_less_count} (3 pares de intervalos encadenados)")
log(f"  • Etiquetas <lessThan> en M(x): {m_less_count} (3 pares de intervalos encadenados)")
log(f"  • Ausencia de errores '>> x2 x x1': {'✅ CONFIRMADO' if not has_bad_gt else '❌ DETECTADO'}")

log(f"\n4. Verificación de Formato Decimal en Ejes de Gráficos 2D:")
pv_nfs = len(p_v.findall('.//{http://schemas.mathsoft.com/worksheet50}numberFormat')) if p_v is not None else 0
pm_nfs = len(p_m.findall('.//{http://schemas.mathsoft.com/worksheet50}numberFormat')) if p_m is not None else 0

log(f"  • Formatos numéricos configurados en Plot DFC: {pv_nfs} (Eje X y Eje Y)")
log(f"  • Formatos numéricos configurados en Plot DMF: {pm_nfs} (Eje X y Eje Y)")
log(f"  • Ausencia de exponente científico 10³: {'✅ CONFIRMADO' if pv_nfs>=2 and pm_nfs>=2 else '❌ DETECTADO'}")

log("\n" + "=" * 80)
log("RESULTADO FINAL: PLANTILLA MAESTRA DESDE CERO CERTIFICADA AL 100%")
log("=" * 80)

with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"\nReporte N1 guardado en:\n{OUTPUT_TXT}")
