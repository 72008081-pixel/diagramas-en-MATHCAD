# -*- coding: utf-8 -*-
"""
CONSTRUCTOR DE LA PLANTILLA MAESTRA DESDE CERO - ESTILO DOCENTE VIGA 2
Crea una plantilla maestra completamente funcional para cualquier ejercicio,
con formulación universal de tramos continuos, límites encadenados e intervalos antes de cada carga.
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
            if sign == '+': acc = el
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

def build_3span_universal_template(base_mcdx_path, out_mcdx_path):
    print(f"\nConstruyendo Plantilla Maestra Desde Cero (3 Tramos Universal):\n-> {out_mcdx_path}")
    files = {}
    with zipfile.ZipFile(base_mcdx_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    root = ET.fromstring(files['mathcad/worksheet.xml'])
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

    # Construir términos universales de 3 tramos (q1, q2, q3) con intervalos al estilo del profesor:
    terms_v = [
        ('+', make_id("V", subscript="A")),
        ('+', make_apply('mult',
              make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=3))),
              make_id("V", subscript="D")))
    ]

    terms_m = [
        ('+', make_apply('mult', make_id("V", subscript="A"), make_id("x"))),
        ('+', make_apply('mult',
              make_apply('mult',
                  make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=3))),
                  make_id("V", subscript="D")),
              make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=3)))))
    ]

    for k in [1, 2, 3]:
        # Condición dentro del tramo: (x_{k-1} < x < x_k)
        cond_in = make_parens(make_apply('lessThan',
            make_apply('lessThan', make_id("x", subscript=k-1), make_id("x")),
            make_id("x", subscript=k)))
        arm_diff = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=k-1)))
        load_in = make_parens(make_apply('mult', make_id("q", subscript=k), arm_diff))
        arm_in = make_parens(make_apply('div', arm_diff, make_real(2)))

        # Condición tramo superado: (x >= x_k)
        cond_sup = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=k)))
        load_sup = make_parens(make_apply('mult', make_id("q", subscript=k), make_id("L", subscript=k)))
        cg_pos = make_parens(make_apply('plus', make_id("x", subscript=k-1), make_apply('div', make_id("L", subscript=k), make_real(2))))
        arm_cg = make_parens(make_apply('minus', make_id("x"), cg_pos))

        # En V(x): Intervalo primero * Carga
        terms_v.append(('-', make_apply('mult', cond_in, load_in)))
        terms_v.append(('-', make_apply('mult', cond_sup, load_sup)))

        # En M(x): Intervalo primero * Carga * Brazo explícito
        terms_m.append(('-', make_apply('mult', make_apply('mult', cond_in, load_in), arm_in)))
        terms_m.append(('-', make_apply('mult', make_apply('mult', cond_sup, load_sup), arm_cg)))

    # 1. Asignar Rango x en top=690.0 (ANTES DE FUNCIONES)
    if r_x is not None:
        r_x.attrib['top'] = '690.0'
        r_x.attrib['left'] = '37.8'

    # 2. Asignar Función Cortante V(x) en top=730.0
    if r_v is not None:
        r_v.attrib['top'] = '730.0'
        r_v.attrib['left'] = '37.8'
        def_el = r_v.find(f'.//{{{ML_NS}}}define')
        if def_el is not None:
            fn_el = def_el.find(f'{{{ML_NS}}}function')
            if fn_el is not None:
                fn_id = fn_el.find(f'{{{ML_NS}}}id')
                if fn_id is not None: fn_id.text = 'V'
            def_el[1] = build_additive_chain(terms_v)

    # 3. Asignar Función Momento M(x) en top=785.0
    if r_m is not None:
        r_m.attrib['top'] = '785.0'
        r_m.attrib['left'] = '37.8'
        def_el = r_m.find(f'.//{{{ML_NS}}}define')
        if def_el is not None:
            def_el[1] = build_additive_chain(terms_m)

    # 4. Asignar Plot V(x) (DFC) en top=860.0
    if p_v is not None:
        p_v.attrib['top'] = '860.0'
        p_v.attrib['left'] = '37.8'
        p_v.attrib['width'] = '680'
        p_v.attrib['height'] = '230'
        plot = p_v.find(tag_ws('plot'))
        if plot is not None:
            for peq in plot.findall(f'.//{{{WS_NS}}}yAxis//{{{WS_NS}}}plotEquation'):
                for el in peq.findall(f'.//{{{ML_NS}}}id'):
                    if el.text == 'Q': el.text = 'V'
            for ax_name in ['xAxis', 'yAxis']:
                ax = plot.find(f'.//{{{WS_NS}}}{ax_name}')
                if ax is not None and ax.find(tag_ws('numberFormat')) is None:
                    nf = ET.SubElement(ax, tag_ws('numberFormat'))
                    ET.SubElement(nf, tag_ws('decimal'), {'precision': '3', 'show-trailing-zeros': 'false', 'radix': 'dec', 'imaginary-value': 'i'})

    # 5. Asignar Plot M(x) (DMF) en top=1130.0
    if p_m is not None:
        p_m.attrib['top'] = '1130.0'
        p_m.attrib['left'] = '37.8'
        p_m.attrib['width'] = '680'
        p_m.attrib['height'] = '230'
        plot = p_m.find(tag_ws('plot'))
        if plot is not None:
            for ax_name in ['xAxis', 'yAxis']:
                ax = plot.find(f'.//{{{WS_NS}}}{ax_name}')
                if ax is not None and ax.find(tag_ws('numberFormat')) is None:
                    nf = ET.SubElement(ax, tag_ws('numberFormat'))
                    ET.SubElement(nf, tag_ws('decimal'), {'precision': '3', 'show-trailing-zeros': 'false', 'radix': 'dec', 'imaginary-value': 'i'})

    # Sanitizer
    for aline in root.iter(tag_ws('axisLine')):
        ptm = aline.attrib.get('positionticmark')
        if ptm is not None:
            try:
                val = float(ptm)
                aline.attrib['positionticmark'] = str(int(round(val)))
            except: pass

    files['mathcad/worksheet.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    with zipfile.ZipFile(out_mcdx_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    print(f"  [OK] Guardada plantilla universal exitosamente: {out_mcdx_path}")

if __name__ == '__main__':
    base_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II"
    comp_dir = os.path.join(base_dir, "01. PLANTILLAS FINALES EXAMENES", "03. MATHCAD", "COMPROBACION")
    src_base = os.path.join(comp_dir, "Viga_3Tramos_Mathcad_Prime_11 (4).mcdx")
    
    # 1. PLANTILLA MAESTRA DESDE CERO (3 Tramos con formulación completa para cualquier ejercicio)
    target_master_3 = os.path.join(comp_dir, "PLANTILLA_MAESTRA_DESDE_CERO_ESTILO_PROFESOR.mcdx")
    build_3span_universal_template(src_base, target_master_3)
    
    # 2. PLANTILLA MAESTRA UNIVERSAL 10 TRAMOS
    src_10 = os.path.join(base_dir, "01. PLANTILLAS FINALES EXAMENES", "03. MATHCAD", "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx")
    target_master_10 = os.path.join(comp_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx")
    shutil.copy2(src_10, target_master_10)
    print(f"Copiada Plantilla Universal 10 Tramos a:\n-> {target_master_10}")
    
    # 3. PLANTILLA VIGA 2 RESUELTA OFICIAL
    target_viga2_solved = os.path.join(comp_dir, "PLANTILLA_VIGA_2_RESUELTA_OFICIAL.mcdx")
    shutil.copy2(src_base, target_viga2_solved)
    print(f"Copiada Plantilla Viga 2 Resuelta Oficial a:\n-> {target_viga2_solved}")
