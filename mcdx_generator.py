"""
=============================================================================
MCDX GENERATOR - CONSTRUCTOR DINÁMICO UNIVERSAL PARA MATHCAD PRIME 11
=============================================================================
Genera archivos nativos .mcdx completamente compatibles con PTC Mathcad Prime 11
utilizando la estructura base validada de 10 tramos y funciones de Macaulay.
Incrusta el esquema vectorial de la viga, cotas, cargas, apoyos y cortes.
"""

import os
import sys
import io
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image

from beam_engine import BeamModel, render_beam_diagram

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
    """Crea un nodo identificador de variable con o sin subíndice."""
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
    """Construye un árbol binario MathML izquierdo para suma y resta algebraica."""
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


def generate_mcdx_for_beam(beam: BeamModel, output_mcdx_path: str, base_template_path: str = None) -> str:
    """
    Construye un archivo .mcdx dinámico compatible al 100% con Mathcad Prime 11.
    Toma la plantilla maestra certificada de 10 tramos y actualiza parámetros,
    diagrama de la viga y funciones de singularidad Macaulay para M(x) y Q(x).
    """
    if base_template_path is None or not os.path.exists(base_template_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_template_path = os.path.join(base_dir, "PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx")

    files = {}
    with zipfile.ZipFile(base_template_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    # 1. Renderizar e incrustar diagrama gráfico vectorial de la viga
    img_beam = render_beam_diagram(beam, width=1400, height=420, show_cuts=True)
    buf_beam = io.BytesIO()
    img_beam.save(buf_beam, format="PNG")
    files['mathcad/media/Image0.png'] = buf_beam.getvalue()

    # 2. Cargar XML del worksheet
    ws_root = ET.fromstring(files['mathcad/worksheet.xml'])
    regs = ws_root[0]

    # A) Actualizar Longitudes L1 a L10 (Regiones 2 a 11)
    spans_10 = beam.spans + [0.0] * (10 - len(beam.spans))
    for i in range(10):
        reg = regs[2 + i]
        for r_el in reg.iter(tag_ml('real')):
            r_el.text = f"{spans_10[i]:g}"

    # B) Actualizar Cargas Distribuidas q1 a q10 (Regiones 25 a 34)
    for i in range(10):
        q_val = beam.distributed_loads.get(i, 0.0)
        reg = regs[25 + i]
        for r_el in reg.iter(tag_ml('real')):
            r_el.text = f"{q_val:g}"

    # C) Actualizar Cargas Puntuales P0 a P10 (Regiones 35 a 45)
    for i in range(11):
        p_val = beam.point_loads.get(i, 0.0)
        reg = regs[35 + i]
        for r_el in reg.iter(tag_ml('real')):
            r_el.text = f"{p_val:g}"

    # D) Actualizar Momentos Aplicados M0 a M10 (Regiones 46 a 56)
    for i in range(11):
        m_val = beam.applied_moments.get(i, 0.0)
        reg = regs[46 + i]
        for r_el in reg.iter(tag_ml('real')):
            r_el.text = f"{m_val:g}"

    # E) Calcular Reacciones y actualizar variables de apoyo
    reactions = beam.calculate_reactions()
    sup_nodes = sorted(beam.supports.keys())
    
    val_va = reactions.get("VA", 0.0)
    val_vd = reactions.get("VD", reactions.get("MA", 0.0))

    # Región 58: VD
    for r_el in regs[58].iter(tag_ml('real')):
        r_el.text = f"{val_vd:.4f}" if isinstance(val_vd, float) else str(val_vd)

    # Región 59: VA
    for r_el in regs[59].iter(tag_ml('real')):
        r_el.text = f"{val_va:.4f}" if isinstance(val_va, float) else str(val_va)

    # F) Construcción Dinámica de Expresiones Macaulay para M(x) y Q(x)
    terms_m = []
    terms_q = []

    # 1. Apoyos y Reacciones
    if len(sup_nodes) >= 2:
        n_a, n_b = sup_nodes[0], sup_nodes[1]
        
        # Apoyo A
        if n_a == 0:
            terms_m.append(('+', make_apply('mult', make_id("V", subscript="A"), make_id("x"))))
            terms_q.append(('+', make_id("V", subscript="A")))
        else:
            cond_va = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=n_a)))
            arm_va = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=n_a)))
            terms_m.append(('+', make_apply('mult', make_apply('mult', cond_va, make_id("V", subscript="A")), arm_va)))
            terms_q.append(('+', make_apply('mult', cond_va, make_id("V", subscript="A"))))

        # Apoyo B
        cond_vb = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=n_b)))
        arm_vb = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=n_b)))
        terms_m.append(('+', make_apply('mult', make_apply('mult', cond_vb, make_id("V", subscript="D")), arm_vb)))
        terms_q.append(('+', make_apply('mult', cond_vb, make_id("V", subscript="D"))))

    elif len(sup_nodes) == 1 and beam.supports[sup_nodes[0]] == 'fixed':
        n_fix = sup_nodes[0]
        # Empotramiento en el origen
        if n_fix == 0:
            terms_m.append(('+', make_id("V", subscript="D")))  # VD actúa como MA
            terms_m.append(('+', make_apply('mult', make_id("V", subscript="A"), make_id("x"))))
            terms_q.append(('+', make_id("V", subscript="A")))
        else:
            cond_fix = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=n_fix)))
            arm_fix = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=n_fix)))
            terms_m.append(('+', make_apply('mult', cond_fix, make_id("V", subscript="D"))))
            terms_m.append(('+', make_apply('mult', make_apply('mult', cond_fix, make_id("V", subscript="A")), arm_fix)))
            terms_q.append(('+', make_apply('mult', cond_fix, make_id("V", subscript="A"))))
    else:
        # Por defecto dos apoyos en 0 y tramo final
        terms_m.append(('+', make_apply('mult', make_id("V", subscript="A"), make_id("x"))))
        terms_q.append(('+', make_id("V", subscript="A")))

    # 2. Cargas Distribuidas
    for k in range(len(beam.spans)):
        q_val = beam.distributed_loads.get(k, 0.0)
        if q_val != 0:
            # Condición de tramo activo: x_(k+1) > x > x_k
            cond_act = make_parens(make_apply('greaterThan',
                make_apply('greaterThan', make_id("x", subscript=k+1), make_id("x")),
                make_id("x", subscript=k)))
            
            if k == 0:
                arm_sq = make_apply('div', make_apply('pow', make_id("x"), make_real(2)), make_real(2))
                arm_v = make_id("x")
            else:
                arm_diff = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=k)))
                arm_sq = make_apply('div', make_apply('pow', arm_diff, make_real(2)), make_real(2))
                arm_v = arm_diff
                
            term_m_act = make_apply('mult', make_apply('mult', cond_act, make_id("q", subscript=k+1)), arm_sq)
            term_q_act = make_apply('mult', make_apply('mult', cond_act, make_id("q", subscript=k+1)), arm_v)
            terms_m.append(('-', term_m_act))
            terms_q.append(('-', term_q_act))

            # Condición de tramo superado: x >= x_(k+1)
            cond_sup = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=k+1)))
            if k == 0:
                arm_cg = make_parens(make_apply('minus', make_id("x"), make_apply('div', make_id("L", subscript=1), make_real(2))))
            else:
                cg_pos = make_parens(make_apply('plus', make_id("x", subscript=k), make_apply('div', make_id("L", subscript=k+1), make_real(2))))
                arm_cg = make_parens(make_apply('minus', make_id("x"), cg_pos))
                
            term_m_sup = make_apply('mult', make_apply('mult', make_apply('mult', cond_sup, make_id("q", subscript=k+1)), make_id("L", subscript=k+1)), arm_cg)
            term_q_sup = make_apply('mult', make_apply('mult', cond_sup, make_id("q", subscript=k+1)), make_id("L", subscript=k+1))
            terms_m.append(('-', term_m_sup))
            terms_q.append(('-', term_q_sup))

    # 3. Momentos Aplicados
    for i in range(len(beam.spans) + 1):
        m_val = beam.applied_moments.get(i, 0.0)
        if m_val != 0:
            if i == 0:
                terms_m.append(('+', make_id("M", subscript=0)))
            else:
                cond_m = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=i)))
                terms_m.append(('+', make_apply('mult', cond_m, make_id("M", subscript=i))))

    # 4. Cargas Puntuales
    for i in range(len(beam.spans) + 1):
        p_val = beam.point_loads.get(i, 0.0)
        if p_val != 0:
            if i == 0:
                terms_m.append(('-', make_apply('mult', make_id("P", subscript=0), make_id("x"))))
                terms_q.append(('-', make_id("P", subscript=0)))
            else:
                cond_p = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=i)))
                arm_p = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=i)))
                term_p_m = make_apply('mult', make_apply('mult', cond_p, make_id("P", subscript=i)), arm_p)
                term_p_q = make_apply('mult', cond_p, make_id("P", subscript=i))
                terms_m.append(('-', term_p_m))
                terms_q.append(('-', term_p_q))

    # Reemplazar definición de M(x) en Región 61
    reg_61_math = regs[61].find(tag_ws('math'))
    reg_61_def = reg_61_math.find(tag_ml('define'))
    reg_61_def[1] = build_additive_chain(terms_m)

    # Reemplazar definición de Q(x) en Región 62
    reg_62_math = regs[62].find(tag_ws('math'))
    reg_62_def = reg_62_math.find(tag_ml('define'))
    reg_62_def[1] = build_additive_chain(terms_q)

    # G) Ajustar dimensiones de la imagen en Región 24
    r24 = regs[24]
    r24.attrib['width'] = '550'
    r24.attrib['height'] = '165'
    png_el = r24.find(f"{tag_ws('picture')}/{tag_ws('png')}")
    if png_el is not None:
        png_el.attrib['display-width'] = '550'
        png_el.attrib['display-height'] = '165'

    # 3. Guardar el archivo XML modificado en el paquete .mcdx
    files['mathcad/worksheet.xml'] = ET.tostring(ws_root, encoding='utf-8', xml_declaration=True)

    output_dir = os.path.dirname(os.path.abspath(output_mcdx_path))
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(output_mcdx_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)

    return output_mcdx_path
