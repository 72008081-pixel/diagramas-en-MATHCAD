# -*- coding: utf-8 -*-
"""
MCDX Suite Updater & Corrector - Estilo Viga 2 (Ing. Alain Elvis Alanoca Aragon)
Implementa rigurosamente el razonamiento y limites/intervalos de Viga 2:
1. x := 0, 0.01 .. Ltot definido ANTES de las funciones de cortante y momento.
2. Intervalo condicional colocado ANTES de la expresion de carga:
   Shear:
     -(xk < x < xk+1) * (qk+1 * (x - xk))
     -(x >= xk+1) * (qk+1 * Lk+1)
   Moment:
     -(xk < x < xk+1) * (qk+1 * (x - xk)) * ((x - xk) / 2)
     -(x >= xk+1) * (qk+1 * Lk+1) * (x - (xk + Lk+1 / 2))
3. Desigualdad encadenada estricta (xk < x < xk+1) con <ml:lessThan>.
4. Funcion de cortante nombrada como V(x) (no Q(x)).
5. Graficos 2D: Plot 1 V(x) vs x, Plot 2 M(x) vs x, con numberFormat decimal limpio.
"""
import os
import sys
import zipfile
import io
import shutil
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

WS_NS = 'http://schemas.mathsoft.com/worksheet50'
ML_NS = 'http://schemas.mathsoft.com/math50'
P_NS = 'http://schemas.microsoft.com/winfx/2006/xaml/presentation'
C_NS = 'clr-namespace:Ptc.Wpf;assembly=Ptc.Core'

ET.register_namespace('', WS_NS)
ET.register_namespace('ml', ML_NS)
ET.register_namespace('p', P_NS)
ET.register_namespace('c', C_NS)

def tag_ws(t): return f'{{{WS_NS}}}{t}'
def tag_ml(t): return f'{{{ML_NS}}}{t}'
def tag_p(t): return f'{{{P_NS}}}{t}'
def tag_c(t): return f'{{{C_NS}}}{t}'

def make_id(name, labels="VARIABLE", is_contextual=True, subscript=None):
    el = ET.Element(tag_ml('id'), {'labels': labels})
    if is_contextual:
        el.attrib['label-is-contextual'] = 'true'
    el.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
    if subscript is not None:
        span = ET.SubElement(el, tag_p('Span'))
        span.text = name
        sub = ET.SubElement(span, tag_c('Subscript'))
        sub.text = str(subscript)
    else:
        el.text = name
    return el

def make_real(val):
    el = ET.Element(tag_ml('real'))
    el.text = f"{val:g}"
    return el

def make_parens(child):
    el = ET.Element(tag_ml('parens'))
    el.append(child)
    return el

def make_apply(op_name, *args):
    el = ET.Element(tag_ml('apply'))
    ET.SubElement(el, tag_ml(op_name))
    for a in args:
        el.append(a)
    return el

def build_additive_chain(terms):
    acc = None
    for sign, el in terms:
        if acc is None:
            if sign == '+':
                acc = el
            else:
                acc = ET.Element(tag_ml('apply'))
                ET.SubElement(acc, tag_ml('minus'))
                acc.append(el)
        else:
            new_acc = ET.Element(tag_ml('apply'))
            op = 'plus' if sign == '+' else 'minus'
            ET.SubElement(new_acc, tag_ml(op))
            new_acc.append(acc)
            new_acc.append(el)
            acc = new_acc
    return acc if acc is not None else make_real(0)

def fix_mcdx_worksheet(xml_bytes, total_l=10.0, q_max=1960.0, q_min=-2100.0, m_max=4950.0, m_min=0.0):
    root = ET.fromstring(xml_bytes)
    regs = root[0]

    # Semantic lookup
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

    # Build exact Viga 2 criteria terms for 3-spans (L1=5, L2=4, L3=1, q2=700, VA=840, VD=1960)
    # V(x) = VA + (x >= x3)*VD - (x1 < x < x2)*(q2*(x - x1)) - (x >= x2)*(q2*L2)
    terms_v = [
        ('+', make_id("V", subscript="A")),
        ('+', make_apply('mult',
              make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=3))),
              make_id("V", subscript="D"))),
        ('-', make_apply('mult',
              make_parens(make_apply('lessThan',
                  make_apply('lessThan', make_id("x", subscript=1), make_id("x")),
                  make_id("x", subscript=2))),
              make_parens(make_apply('mult',
                  make_id("q", subscript=2),
                  make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=1))))))),
        ('-', make_apply('mult',
              make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=2))),
              make_parens(make_apply('mult',
                  make_id("q", subscript=2),
                  make_id("L", subscript=2)))))
    ]

    # M(x) = VA*x + (x >= x3)*VD*(x - x3) - (x1 < x < x2)*(q2*(x - x1))*((x - x1)/2) - (x >= x2)*(q2*L2)*(x - (x1 + L2/2))
    arm_diff = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=1)))
    arm_in = make_parens(make_apply('div', arm_diff, make_real(2)))
    cg_pos = make_parens(make_apply('plus', make_id("x", subscript=1), make_apply('div', make_id("L", subscript=2), make_real(2))))
    arm_cg = make_parens(make_apply('minus', make_id("x"), cg_pos))

    terms_m = [
        ('+', make_apply('mult', make_id("V", subscript="A"), make_id("x"))),
        ('+', make_apply('mult',
              make_apply('mult',
                  make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=3))),
                  make_id("V", subscript="D")),
              make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=3))))),
        ('-', make_apply('mult',
              make_apply('mult',
                  make_parens(make_apply('lessThan',
                      make_apply('lessThan', make_id("x", subscript=1), make_id("x")),
                      make_id("x", subscript=2))),
                  make_parens(make_apply('mult', make_id("q", subscript=2), arm_diff))),
              arm_in)),
        ('-', make_apply('mult',
              make_apply('mult',
                  make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=2))),
                  make_parens(make_apply('mult', make_id("q", subscript=2), make_id("L", subscript=2)))),
              arm_cg))
    ]

    # 1. Apply to r_x (Range variable x) - PLACED BEFORE FUNCTIONS at top=690.0!
    if r_x is not None:
        r_x.attrib['top'] = '690.0'
        r_x.attrib['left'] = '37.8'

    # 2. Apply to r_v (Shear function) - top=730.0
    if r_v is not None:
        def_el = r_v.find(f'.//{{{ML_NS}}}define')
        if def_el is not None:
            # ensure func name V
            fn_el = def_el.find(f'{{{ML_NS}}}function')
            if fn_el is not None:
                fn_id = fn_el.find(f'{{{ML_NS}}}id')
                if fn_id is not None:
                    fn_id.text = 'V'
            def_el[1] = build_additive_chain(terms_v)
        r_v.attrib['top'] = '730.0'
        r_v.attrib['left'] = '37.8'

    # 3. Apply to r_m (Moment function) - top=785.0
    if r_m is not None:
        def_el = r_m.find(f'.//{{{ML_NS}}}define')
        if def_el is not None:
            def_el[1] = build_additive_chain(terms_m)
        r_m.attrib['top'] = '785.0'
        r_m.attrib['left'] = '37.8'

    # 4. Configure Plot V(x) (DFC) - top=860.0
    if p_v is not None:
        p_v.attrib['top'] = '860.0'
        p_v.attrib['left'] = '37.8'
        p_v.attrib['width'] = '680'
        p_v.attrib['height'] = '230'
        plot = p_v.find(tag_ws('plot'))
        if plot is not None:
            # Set y-axis equation to V(x)
            for peq in plot.findall(f'.//{{{WS_NS}}}yAxis//{{{WS_NS}}}plotEquation'):
                for el in peq.findall(f'.//{{{ML_NS}}}id'):
                    if el.text == 'Q':
                        el.text = 'V'
            # numberFormat for both axes
            for ax_name in ['xAxis', 'yAxis']:
                ax = plot.find(f'.//{{{WS_NS}}}{ax_name}')
                if ax is not None:
                    if ax.find(tag_ws('numberFormat')) is None:
                        nf = ET.SubElement(ax, tag_ws('numberFormat'))
                        ET.SubElement(nf, tag_ws('decimal'), {
                            'precision': '3',
                            'show-trailing-zeros': 'false',
                            'radix': 'dec',
                            'imaginary-value': 'i'
                        })

    # 5. Configure Plot M(x) (DMF) - top=1130.0
    if p_m is not None:
        p_m.attrib['top'] = '1130.0'
        p_m.attrib['left'] = '37.8'
        p_m.attrib['width'] = '680'
        p_m.attrib['height'] = '230'
        plot = p_m.find(tag_ws('plot'))
        if plot is not None:
            for ax_name in ['xAxis', 'yAxis']:
                ax = plot.find(f'.//{{{WS_NS}}}{ax_name}')
                if ax is not None:
                    if ax.find(tag_ws('numberFormat')) is None:
                        nf = ET.SubElement(ax, tag_ws('numberFormat'))
                        ET.SubElement(nf, tag_ws('decimal'), {
                            'precision': '3',
                            'show-trailing-zeros': 'false',
                            'radix': 'dec',
                            'imaginary-value': 'i'
                        })

    # Sanitizer: positionticmark xs:integer
    for aline in root.iter(tag_ws('axisLine')):
        ptm = aline.attrib.get('positionticmark')
        if ptm is not None:
            try:
                val = float(ptm)
                aline.attrib['positionticmark'] = str(int(round(val)))
            except:
                pass

    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

def process_file(in_path, out_path):
    print(f"Procesando: {in_path} -> {out_path}")
    files = {}
    with zipfile.ZipFile(in_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)
    
    files['mathcad/worksheet.xml'] = fix_mcdx_worksheet(files['mathcad/worksheet.xml'])
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    print(f"  OK: {out_path} guardado con exito.")

if __name__ == '__main__':
    base_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II"
    comp_dir = os.path.join(base_dir, "01. PLANTILLAS FINALES EXAMENES", "03. MATHCAD", "COMPROBACION")
    
    # Target in COMPROBACION
    target_4 = os.path.join(comp_dir, "Viga_3Tramos_Mathcad_Prime_11 (4).mcdx")
    target_clean = os.path.join(comp_dir, "Viga_3Tramos_Mathcad_Prime_11.mcdx")
    target_viga2_template = os.path.join(comp_dir, "PLANTILLA_VIGA_ESTILO_VIGA2_OFICIAL.mcdx")
    
    # 1. Update Viga_3Tramos_Mathcad_Prime_11 (4).mcdx in place
    process_file(target_4, target_4)
    # 2. Also create clean copies
    process_file(target_4, target_clean)
    process_file(target_4, target_viga2_template)
    
    # 3. Copy exact teacher file as VIGA_2_EJEMPLO_PROFESOR_ALAIN_ALANOCA.mcdx
    teacher_mcdx = os.path.join(base_dir, "01. PLANTILLAS FINALES EXAMENES", "PLANTILLAS", "EJERCIO DEL PDF.mcdx")
    dest_teacher = os.path.join(comp_dir, "VIGA_2_EJEMPLO_PROFESOR_ALAIN_ALANOCA.mcdx")
    if os.path.exists(teacher_mcdx):
        shutil.copy2(teacher_mcdx, dest_teacher)
        print(f"Copiado ejemplo exacto del docente a: {dest_teacher}")
    
    print("\nTODOS LOS ARCHIVOS EN COMPROBACION ACTUALIZADOS AL ESTILO VIGA 2.")
