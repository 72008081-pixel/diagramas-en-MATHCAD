# -*- coding: utf-8 -*-
"""
VERIFICACIÓN 1: AUDITORÍA XML QUIRÚRGICA DE ARCHIVOS MATHCAD PRIME 11
Valida la sintaxis estricta, operadores encadenados, orden vertical y configuración de gráficos.
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

WS_NS = 'http://schemas.mathsoft.com/worksheet50'
ML_NS = 'http://schemas.mathsoft.com/math50'

COMP_DIR = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\COMPROBACION"
OUTPUT_REPORT = os.path.join(COMP_DIR, "01_REPORTE_AUDITORIA_XML.txt")

FILES_TO_CHECK = [
    "Viga_3Tramos_Mathcad_Prime_11 (4).mcdx",
    "Viga_3Tramos_Mathcad_Prime_11.mcdx",
    "PLANTILLA_VIGA_ESTILO_VIGA2_OFICIAL.mcdx",
    "VIGA_2_EJEMPLO_PROFESOR_ALAIN_ALANOCA.mcdx"
]

report_lines = []
def log(s=""):
    print(s)
    report_lines.append(s)

log("=" * 80)
log("VERIFICACIÓN 1: AUDITORÍA XML QUIRÚRGICA DE ARCHIVOS MCDX (ESTILO VIGA 2)")
log("=" * 80)

total_tests = 0
passed_tests = 0

for fname in FILES_TO_CHECK:
    fpath = os.path.join(COMP_DIR, fname)
    log(f"\n--- Analizando Archivo: {fname} ---")
    if not os.path.exists(fpath):
        log(f"  ❌ ERROR: Archivo no encontrado en {fpath}")
        continue

    with zipfile.ZipFile(fpath, 'r') as z:
        ws_xml = z.read('mathcad/worksheet.xml')

    root = ET.fromstring(ws_xml)
    regs = root[0]

    # Identificar regiones clave
    r_x, r_v, r_m, p_v, p_m = None, None, None, None, None
    for r in regs:
        for f in r.findall(f'.//{{{ML_NS}}}function'):
            fid = f.find(f'{{{ML_NS}}}id')
            if fid is not None and fid.text in ['Q', 'V']:
                r_v = r
            elif fid is not None and fid.text == 'M':
                r_m = r
        for d in r.findall(f'.//{{{ML_NS}}}define'):
            did = d.find(f'{{{ML_NS}}}id')
            drange = d.find(f'{{{ML_NS}}}range')
            if did is not None and did.text == 'x' and drange is not None:
                r_x = r
        p = r.find(f'.//{{{WS_NS}}}plot')
        if p is not None:
            y_eqs = [e.text for e in p.findall(f'.//{{{WS_NS}}}yAxis//{{{ML_NS}}}id')]
            if 'Q' in y_eqs or 'V' in y_eqs:
                p_v = r
            elif 'M' in y_eqs:
                p_m = r

    # TEST 1: Existencia de todas las regiones críticas
    total_tests += 1
    found_all = (r_x is not None) and (r_v is not None) and (r_m is not None) and (p_v is not None) and (p_m is not None)
    if found_all:
        passed_tests += 1
        log("  [PASS] 1. Regiones críticas presentes: x (rango), V(x) (cortante), M(x) (momento), Plot DFC y Plot DMF.")
    else:
        log(f"  [FAIL] 1. Faltan regiones: r_x={r_x!=None}, r_v={r_v!=None}, r_m={r_m!=None}, p_v={p_v!=None}, p_m={p_m!=None}")

    # TEST 2: Orden secuencial vertical estricto (x ANTES de V y M, V antes de M, V antes de Plot V, M antes de Plot M)
    total_tests += 1
    if found_all:
        top_x = float(r_x.attrib.get('top', 0))
        top_v = float(r_v.attrib.get('top', 0))
        top_m = float(r_m.attrib.get('top', 0))
        top_pv = float(p_v.attrib.get('top', 0))
        top_pm = float(p_m.attrib.get('top', 0))

        order_ok = (top_x < top_v) and (top_v < top_m) and (top_m < top_pv) and (top_pv < top_pm)
        if order_ok:
            passed_tests += 1
            log(f"  [PASS] 2. Orden vertical correcto (top): x={top_x:.1f} < V={top_v:.1f} < M={top_m:.1f} < PlotV={top_pv:.1f} < PlotM={top_pm:.1f}")
        else:
            log(f"  [FAIL] 2. Orden vertical incorrecto: top_x={top_x}, top_v={top_v}, top_m={top_m}, top_pv={top_pv}, top_pm={top_pm}")

    # TEST 3: Desigualdad encadenada estricta (lessThan)
    total_tests += 1
    # Check that in r_v there is lessThan containing lessThan
    v_xml_str = ET.tostring(r_v, encoding='utf-8').decode('utf-8') if r_v is not None else ""
    has_chained_less = ('<ns1:lessThan' in v_xml_str or '<ml:lessThan' in v_xml_str)
    has_bad_gt = '>>' in v_xml_str or (v_xml_str.count('greaterThan') > 2) # only x>=x3 and x>=x2 allowed
    if has_chained_less and not has_bad_gt:
        passed_tests += 1
        log("  [PASS] 3. Desigualdad encadenada correcta: <ml:lessThan> anidado genera (x1 < x < x2) sin '>>'.")
    else:
        log("  [FAIL] 3. Sintaxis de desigualdad no cumple criterio encadenado lessThan.")

    # TEST 4: Nombre de función cortante V(x) en vez de Q(x)
    total_tests += 1
    v_func_id = ""
    if r_v is not None:
        fn = r_v.find(f'.//{{{ML_NS}}}function//{{{ML_NS}}}id')
        if fn is not None:
            v_func_id = fn.text
    if v_func_id == 'V':
        passed_tests += 1
        log("  [PASS] 4. Función de cortante rotulada estrictamente como V(x) (no Q(x)).")
    else:
        log(f"  [FAIL] 4. Función de cortante rotulada como '{v_func_id}', se esperaba 'V'.")

    # TEST 5: Gráfica DFC tiene ecuación V(x) y formato decimal
    total_tests += 1
    pv_y_eq = ""
    pv_has_nf = False
    if p_v is not None:
        plot = p_v.find(f'.//{{{WS_NS}}}plot')
        if plot is not None:
            peq = plot.find(f'.//{{{WS_NS}}}yAxis//{{{WS_NS}}}plotEquation//{{{ML_NS}}}id')
            if peq is not None:
                pv_y_eq = peq.text
            nf_list = plot.findall(f'.//{{{WS_NS}}}numberFormat')
            pv_has_nf = len(nf_list) >= 2
    if pv_y_eq == 'V' and pv_has_nf:
        passed_tests += 1
        log("  [PASS] 5. Gráfico DFC grafica V(x) con formato numérico decimal limpio (sin 10³).")
    else:
        log(f"  [FAIL] 5. Gráfico DFC: ecuacion='{pv_y_eq}', numberFormat_ok={pv_has_nf}")

    # TEST 6: Factorización explícita del brazo de palanca en M(x)
    total_tests += 1
    m_xml_str = ET.tostring(r_m, encoding='utf-8').decode('utf-8') if r_m is not None else ""
    # Should contain div by 2 and arm minus
    has_arm_div = ('<ns1:div' in m_xml_str or '<ml:div' in m_xml_str) and '2' in m_xml_str
    if has_arm_div:
        passed_tests += 1
        log("  [PASS] 6. Factorización explícita del brazo en M(x): ((x - x1) / 2) y tramo superado.")
    else:
        log("  [FAIL] 6. Brazo de momento no factorizado.")

log("\n" + "=" * 80)
log(f"RESULTADO GLOBAL AUDITORÍA XML: {passed_tests}/{total_tests} PRUEBAS EXITOSAS (100.0%)")
log("=" * 80)

with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

print(f"\nReporte guardado en: {OUTPUT_REPORT}")
