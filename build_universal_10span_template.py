# -*- coding: utf-8 -*-
"""
CONSTRUCTOR DEFINITIVO DE LA PLANTILLA UNIVERSAL 10 TRAMOS ESTILO INGENIERO
Genera 'PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx' con formulación completa
para los 10 tramos (q1..q10, P1..P10, M1..M10), con la sintaxis exacta del profesor Alain Alanoca:
- Vector de rango x definido ANTES de las funciones (top=690.0)
- Intervalo antepuesto: (x_(k-1) < x < x_k) * [q_k * (x - x_(k-1))]
- Brazo de momento explícito: ((x - x_(k-1)) / 2) y (x - (x_(k-1) + L_k/2))
- Sin errores de operador '>>', 100% compatible con Mathcad Prime 7, 8, 9, 10 y 11.
"""
import os
import sys
import zipfile
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

def generate_10span_template(src_base_path, dest_path):
    print(f"Generando plantilla 10 tramos universal estilo ingeniero:\nOrigen: {src_base_path}\nDestino: {dest_path}")
    files = {}
    with zipfile.ZipFile(src_base_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    root = ET.fromstring(files['mathcad/worksheet.xml'])
    regs = root[0]

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

    # Reacciones: VA en x=0, y VD en x10 (apoyo derecho general)
    terms_v = [
        ('+', make_id("V", subscript="A")),
        ('+', make_apply('mult',
              make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=10))),
              make_id("V", subscript="D")))
    ]

    terms_m = [
        ('+', make_apply('mult', make_id("V", subscript="A"), make_id("x"))),
        ('+', make_apply('mult',
              make_apply('mult',
                  make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=10))),
                  make_id("V", subscript="D")),
              make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=10)))))
    ]

    # Agregar los 10 tramos con intervalos y brazos estilo profesor Alain Alanoca:
    for k in range(1, 11):
        # 1. Carga distribuida q_k:
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

        # 2. Carga puntual P_k (en nudo x_k):
        cond_pk = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=k)))
        terms_v.append(('-', make_apply('mult', cond_pk, make_id("P", subscript=k))))
        terms_m.append(('-', make_apply('mult', make_apply('mult', cond_pk, make_id("P", subscript=k)),
                                        make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=k))))))

        # 3. Momento concentrado M_k (en nudo x_k):
        terms_m.append(('-', make_apply('mult', cond_pk, make_id("M", subscript=k))))

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

    # Sanitizar marcas de tics
    for aline in root.iter(tag_ws('axisLine')):
        ptm = aline.attrib.get('positionticmark')
        if ptm is not None:
            try:
                val = float(ptm)
                aline.attrib['positionticmark'] = str(int(round(val)))
            except: pass

    files['mathcad/worksheet.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    print(f"✅ Guardado exitoso: {dest_path}")

if __name__ == '__main__':
    base_dir = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD"
    src = os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx")
    
    # 1. En carpeta COMPROBACION
    dest_comp = os.path.join(base_dir, "COMPROBACION", "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx")
    generate_10span_template(src, dest_comp)
    
    # 2. En raiz de 03. MATHCAD (repositorio diagramas-en-MATHCAD)
    dest_root = os.path.join(base_dir, "PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx")
    generate_10span_template(src, dest_root)
    
    # 3. En AUTOMATIZACION ARMADURAS Y VIGAS\mathcad (repositorio Ulianov-Continental)
    dest_suite = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad\PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"
    generate_10span_template(src, dest_suite)
