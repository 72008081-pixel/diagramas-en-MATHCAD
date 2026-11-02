# -*- coding: utf-8 -*-
"""
REPARADOR Y CERTIFICADOR DE ESQUEMA XML PARA TODAS LAS PLANTILLAS .MCDX
Corrige la posición de 'numberFormat' para que esté estrictamente antes de 'plotEquations'
y elimina 'Typography.Variants' para evitar excepciones de XamlReader en Mathcad Prime 11.
"""
import os
import sys
import zipfile
import re
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

WS_NS = 'http://schemas.mathsoft.com/worksheet50'
def tag_ws(t): return f'{{{WS_NS}}}{t}'

def fix_mcdx_file(path):
    if not os.path.exists(path):
        return False
        
    print(f"Reparando esquema XSD en: {path}")
    files = {}
    with zipfile.ZipFile(path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    # 1. Eliminar Typography.Variants en todos los archivos xml
    for name in list(files.keys()):
        if name.endswith('.xml'):
            txt = files[name].decode('utf-8', errors='ignore')
            txt = re.sub(r'\s*Typography\.[a-zA-Z0-9]+="[^"]*"', '', txt)
            files[name] = txt.encode('utf-8')

    root = ET.fromstring(files['mathcad/worksheet.xml'])

    # 2. Reordenar estrictamente los elementos de xAxis y yAxis según el esquema XSD:
    # xs:sequence: axisLine, axisGrid, axisLabel, markers, numberFormat, plotEquations, xyDomain
    for ax_tag in ['xAxis', 'yAxis']:
        for ax in root.iter(f'{{{WS_NS}}}{ax_tag}'):
            for nf in list(ax.findall(f'{{{WS_NS}}}numberFormat')):
                ax.remove(nf)
            
            nf = ET.Element(tag_ws('numberFormat'))
            ET.SubElement(nf, tag_ws('decimal'), {
                'precision': '3',
                'show-trailing-zeros': 'false',
                'radix': 'dec',
                'imaginary-value': 'i'
            })
            
            idx = None
            for i, child in enumerate(ax):
                if child.tag.endswith('plotEquations'):
                    idx = i
                    break
            if idx is not None:
                ax.insert(idx, nf)
            else:
                ax.append(nf)

    # 3. Sanitizar positionticmark (debe ser xs:integer)
    for aline in root.iter(f'{{{WS_NS}}}axisLine'):
        ptm = aline.attrib.get('positionticmark')
        if ptm is not None:
            try:
                val = float(ptm)
                aline.attrib['positionticmark'] = str(int(round(val)))
            except:
                pass

    files['mathcad/worksheet.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
            
    print(f"  -> [OK] Reparado y guardado: {path}")
    return True

if __name__ == '__main__':
    base_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD"
    comp_dir = os.path.join(base_dir, "COMPROBACION")
    suite_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad"
    visit_dir = r"D:\Visitante\Documents"

    targets = [
        os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx"),
        os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx"),
        os.path.join(base_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"),
        os.path.join(base_dir, "EJERCICIO-01.mcdx"),
        os.path.join(comp_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"),
        os.path.join(comp_dir, "PLANTILLA_MAESTRA_DESDE_CERO_ESTILO_PROFESOR.mcdx"),
        os.path.join(comp_dir, "PLANTILLA_VIGA_2_RESUELTA_OFICIAL.mcdx"),
        os.path.join(suite_dir, "PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx"),
        os.path.join(suite_dir, "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx"),
        os.path.join(suite_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"),
        os.path.join(visit_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"),
    ]

    for t in targets:
        if os.path.exists(t):
            fix_mcdx_file(t)
