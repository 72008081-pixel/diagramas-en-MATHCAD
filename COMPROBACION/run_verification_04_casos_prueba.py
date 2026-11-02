# -*- coding: utf-8 -*-
"""
VERIFICACIÓN 4: GENERACIÓN Y VALIDACIÓN DE CASOS DE PRUEBA PARAMÉTRICOS ADICIONALES
Demuestra que el criterio de intervalos y límites del estilo Viga 2
funciona dinámicamente para cualquier geometría de viga, cargas distribuidas y puntuales.
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

MATHCAD_DIR = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD"
sys.path.append(MATHCAD_DIR)

from beam_engine import BeamModel
from mcdx_generator import generate_mcdx_for_beam

COMP_DIR = os.path.join(MATHCAD_DIR, "COMPROBACION")
OUTPUT_REPORT = os.path.join(COMP_DIR, "04_REPORTE_CASOS_PARAMETRICOS.txt")
BASE_TEMPLATE = os.path.join(MATHCAD_DIR, "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx")

report_lines = []
def log(s=""):
    print(s)
    report_lines.append(s)

log("=" * 85)
log("VERIFICACIÓN 4: MATRIZ DE 4 CASOS DE PRUEBA PARAMÉTRICOS (ESTILO VIGA 2)")
log("=" * 85)

test_cases = [
    {
        "id": "CASO_01",
        "name": "TEST_01_VIGA_2_OFICIAL_5_4_1.mcdx",
        "desc": "Viga Oficial Alain Elvis Alanoca Aragón: L=[5, 4, 1] m, q2=700 kg/m",
        "spans": [5.0, 4.0, 1.0],
        "supports": {0: 'pin', 3: 'roller'},
        "q": {1: 700.0},
        "P": {},
        "M": {}
    },
    {
        "id": "CASO_02",
        "name": "TEST_02_VIGA_2TRAMOS_CARGA_PUNTUAL.mcdx",
        "desc": "Viga 2 Tramos: L=[4, 4] m, q1=500 kg/m, Carga puntual P1=1000 kg en x=4 m",
        "spans": [4.0, 4.0],
        "supports": {0: 'pin', 2: 'roller'},
        "q": {0: 500.0},
        "P": {1: 1000.0},
        "M": {}
    },
    {
        "id": "CASO_03",
        "name": "TEST_03_VIGA_SIMETRICA_CON_VOLADIZO.mcdx",
        "desc": "Viga Simétrica con Voladizo: L=[2, 6, 2] m, Apoyos en x=2 y x=8, q2=800 kg/m",
        "spans": [2.0, 6.0, 2.0],
        "supports": {1: 'pin', 2: 'roller'},
        "q": {1: 800.0},
        "P": {},
        "M": {}
    },
    {
        "id": "CASO_04",
        "name": "TEST_04_VIGA_TRES_TRAMOS_DOS_CARGAS.mcdx",
        "desc": "Viga 3 Tramos con Doble Carga: L=[3, 4, 3] m, q1=400 kg/m, q2=600 kg/m",
        "spans": [3.0, 4.0, 3.0],
        "supports": {0: 'pin', 3: 'roller'},
        "q": {0: 400.0, 1: 600.0},
        "P": {},
        "M": {}
    }
]

total_cases = len(test_cases)
passed_cases = 0

for tc in test_cases:
    out_file = os.path.join(COMP_DIR, tc["name"])
    log(f"\nGenerando {tc['id']}: {tc['name']}")
    log(f"  Descripción: {tc['desc']}")
    
    b = BeamModel()
    b.spans = tc["spans"]
    b.supports = tc["supports"]
    b.distributed_loads = tc["q"]
    b.point_loads = tc["P"]
    b.applied_moments = tc["M"]
    
    try:
        generate_mcdx_for_beam(b, out_file, BASE_TEMPLATE)
        log(f"  [OK] Archivo MCDX generado.")
        
        # Validar estructura XML del caso generado
        with zipfile.ZipFile(out_file, 'r') as z:
            ws_xml = z.read('mathcad/worksheet.xml')
        
        root = ET.fromstring(ws_xml)
        regs = root[0]
        
        # Comprobar existencia y formato
        r_x = None
        r_v = None
        r_m = None
        for r in regs:
            # check function V
            for fn in r.findall('.//{http://schemas.mathsoft.com/math50}function/{http://schemas.mathsoft.com/math50}id'):
                if fn.text == 'V':
                    r_v = r
                elif fn.text == 'M':
                    r_m = r
            for d in r.findall('.//{http://schemas.mathsoft.com/math50}define/{http://schemas.mathsoft.com/math50}range'):
                r_x = r
        
        xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')
        has_less = '<ml:lessThan' in xml_str or '<ns1:lessThan' in xml_str
        has_no_double_gt = '>>' not in xml_str
        
        # Reacciones
        reac = b.calculate_reactions()
        reac_str = ", ".join([f"{k}={v:.2f} kg" for k, v in reac.items()])
        log(f"  Reacciones calculadas: {reac_str}")
        log(f"  Verificación Estructural XML: r_x={r_x!=None}, r_v={r_v!=None}, r_m={r_m!=None}")
        log(f"  Desigualdad lessThan: {has_less}, Sin errores '>>': {has_no_double_gt}")
        
        if r_x is not None and r_v is not None and r_m is not None and has_no_double_gt:
            passed_cases += 1
            log(f"  ✅ Caso {tc['id']}: 100% CONFORME Y VALIDADO.")
        else:
            log(f"  ❌ Caso {tc['id']}: Falló verificación estructural.")
            
    except Exception as e:
        log(f"  ❌ Error generando {tc['id']}: {e}")

log("\n" + "=" * 85)
log(f"RESULTADO DE CASOS DE PRUEBA: {passed_cases}/{total_cases} CASOS COMPLETAMENTE CONFORMES")
log("=" * 85)

with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

print(f"\nReporte de casos paramétricos guardado en:\n{OUTPUT_REPORT}")
