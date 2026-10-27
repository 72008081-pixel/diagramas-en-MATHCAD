"""
=============================================================================
MCDX GENERATOR - CONSTRUCTOR DE ARCHIVOS NATIVOS PARA PTC MATHCAD PRIME 11
=============================================================================
Ensambla el paquete OPC ZIP (.mcdx) con regiones matemáticas, esquemas MathML,
imágenes vectoriales embebidas y gráficos XY dinámicos.
"""

import os
import sys
import zipfile
import io
import shutil
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

def make_id(name, labels="VARIABLE", is_contextual=False, subscript=None):
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

def make_scaled(val, unit_str):
    apply_el = ET.Element(tag_ml('apply'))
    ET.SubElement(apply_el, tag_ml('scale'))
    apply_el.append(make_real(val))
    if '/' in unit_str:
        num, den = unit_str.split('/')
        div_el = ET.SubElement(apply_el, tag_ml('apply'))
        ET.SubElement(div_el, tag_ml('div'))
        div_el.append(make_id(num, labels='UNIT', is_contextual=True))
        div_el.append(make_id(den, labels='UNIT', is_contextual=True))
    elif '*' in unit_str:
        p1, p2 = unit_str.split('*')
        mult_el = ET.SubElement(apply_el, tag_ml('apply'))
        ET.SubElement(mult_el, tag_ml('mult'))
        mult_el.append(make_id(p1, labels='UNIT', is_contextual=True))
        mult_el.append(make_id(p2, labels='UNIT', is_contextual=True))
    else:
        apply_el.append(make_id(unit_str, labels='UNIT', is_contextual=True))
    return apply_el

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

def make_define(target, expr):
    el = ET.Element(tag_ml('define'))
    el.append(target)
    el.append(expr)
    return el

def make_region_math(reg_id, top, left, math_child):
    reg = ET.Element(tag_ws('region'), {
        'region-id': str(reg_id),
        'top': f'{top:.1f}',
        'left': f'{left:.1f}'
    })
    m = ET.SubElement(reg, tag_ws('math'))
    m.append(math_child)
    return reg

def make_xaml_package(text, font_size=16, is_bold=True, bg_color='#FFFFF200'):
    bold_str = 'FontWeight="Bold"' if is_bold else ''
    xaml = f'<Section xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xml:space="preserve" TextAlignment="Left" LineHeight="Auto" IsHyphenationEnabled="False" xml:lang="es-pe" FlowDirection="LeftToRight" FontFamily="Segoe UI" FontSize="{font_size}" {bold_str} Foreground="#FF000000"><Paragraph><Run Background="{bg_color}">{text}</Run></Paragraph></Section>'
    
    rels = '<?xml version="1.0" encoding="utf-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships" />'
    ct = '<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" /><Default Extension="xaml" ContentType="application/xaml+xml" /></Types>'
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('Xaml/Document.xaml', xaml.encode('utf-8'))
        z.writestr('_rels/.rels', rels.encode('utf-8'))
        z.writestr('[Content_Types].xml', ct.encode('utf-8'))
    return buf.getvalue()


def generate_mcdx_for_beam(beam: BeamModel, output_mcdx_path: str, base_template_path: str) -> str:
    """Construye un archivo .mcdx completamente estructurado e incrusta el diagrama de la viga."""
    files = {}
    with zipfile.ZipFile(base_template_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    # 1. Generar la imagen del esquema de la viga y agregarla al paquete
    beam_img = render_beam_diagram(beam, width=1400, height=450, show_cuts=True)
    img_buf = io.BytesIO()
    beam_img.save(img_buf, format="PNG")
    img_bytes = img_buf.getvalue()
    files['mathcad/media/Image_Beam.png'] = img_bytes

    # 2. Reconstruir worksheet.xml
    ws_root = ET.fromstring(files['mathcad/worksheet.xml'])
    regions_parent = ws_root[0]
    
    # Extraer plantillas de gráficos originales
    plot_q_orig = None
    plot_m_orig = None
    for r in list(regions_parent):
        if r.attrib.get('region-id') == '29':
            plot_q_orig = r
        elif r.attrib.get('region-id') == '30':
            plot_m_orig = r

    regions_parent.clear()
    reg_id_counter = 0

    # Secciones de texto
    sections = [
        ("ANÁLISIS ESTRUCTURAL II — DIAGRAMAS EN MATHCAD (MÉTODO DE MACAULAY)", 17, True, "#FFFFF200"),
        ("1. GEOMETRÍA Y DISCRETIZACIÓN DE LA VIGA:", 13, True, "#FFE0E0E0"),
        ("ESQUEMA ESTRUCTURAL DE LA VIGA Y CORTES DE SECCIÓN:", 13, True, "#FFE0E0E0"),
        ("2. CARGAS APLICADAS (DISTRIBUIDAS, PUNTUALES Y MOMENTOS):", 13, True, "#FFE0E0E0"),
        ("3. CÁLCULO DE REACCIONES DE APOYO:", 13, True, "#FFE0E0E0"),
        ("4. FUNCIONES DE SECCIÓN: MOMENTO M(x) Y CORTANTE Q(x):", 13, True, "#FFE0E0E0"),
        ("5. RANGO DE EVALUACIÓN MILIMÉTRICO:", 13, True, "#FFE0E0E0"),
        ("6. DIAGRAMAS DE FUERZA CORTANTE (DFC) Y MOMENTO FLECTOR (DMF):", 13, True, "#FFE0E0E0")
    ]

    # Crear paquetes XAML y registrar relaciones
    rels_xml = '<?xml version="1.0" encoding="utf-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    for idx, (sec_text, fsize, is_bold, bg) in enumerate(sections):
        pkg_path = f"mathcad/xaml/FlowDocument{idx}.XamlPackage"
        files[pkg_path] = make_xaml_package(sec_text, fsize, is_bold, bg)
        rels_xml += f'<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/flowDocument" Target="/{pkg_path}" Id="RelFlowDoc{idx}" />'
    
    # Relación de la imagen
    rels_xml += '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="/mathcad/media/Image_Beam.png" Id="RelImageBeam" />'
    rels_xml += '</Relationships>'
    files['mathcad/_rels/worksheet.xml.rels'] = rels_xml.encode('utf-8')

    cur_top = 20.0
    left_margin = 37.8

    def add_text_reg(sec_idx, top_offset=30.0):
        nonlocal reg_id_counter, cur_top
        cur_top += top_offset
        r = ET.Element(tag_ws('region'), {
            'region-id': str(reg_id_counter),
            'top': f'{cur_top:.1f}',
            'left': f'{left_margin:.1f}'
        })
        ET.SubElement(r, tag_ws('text'), {'item-idref': f'RelFlowDoc{sec_idx}'})
        regions_parent.append(r)
        reg_id_counter += 1

    def add_math(math_child, top=None, left=None):
        nonlocal reg_id_counter, cur_top
        if top is None:
            top = cur_top
        if left is None:
            left = left_margin
        r = make_region_math(reg_id_counter, top, left, math_child)
        regions_parent.append(r)
        reg_id_counter += 1

    # Título principal
    add_text_reg(0, top_offset=10.0)

    # 1. Geometría
    add_text_reg(1, top_offset=30.0)

    # Definir longitudes de tramos (hasta 10)
    cur_top += 25.0
    all_spans = beam.spans + [0.0] * (10 - len(beam.spans))
    # Fila 1 (L1 a L5)
    for i in range(5):
        def_L = make_define(make_id("L", subscript=i+1), make_scaled(all_spans[i], beam.unit_length))
        add_math(def_L, top=cur_top, left=left_margin + i * 115.0)

    # Fila 2 (L6 a L10)
    cur_top += 28.0
    for i in range(5, 10):
        def_L = make_define(make_id("L", subscript=i+1), make_scaled(all_spans[i], beam.unit_length))
        add_math(def_L, top=cur_top, left=left_margin + (i - 5) * 115.0)

    # Nodos acumulados x0 a x10
    cur_top += 30.0
    # x0 := 0 m
    add_math(make_define(make_id("x", subscript=0), make_scaled(0.0, beam.unit_length)), top=cur_top, left=left_margin)
    for i in range(1, 5):
        if i == 1:
            expr = make_id("L", is_contextual=True, subscript=1)
        else:
            expr = make_apply('plus', make_id("x", is_contextual=True, subscript=i-1), make_id("L", is_contextual=True, subscript=i))
        add_math(make_define(make_id("x", subscript=i), expr), top=cur_top, left=left_margin + i * 115.0)

    cur_top += 28.0
    for i in range(5, 11):
        expr = make_apply('plus', make_id("x", is_contextual=True, subscript=i-1), make_id("L", is_contextual=True, subscript=i))
        add_math(make_define(make_id("x", subscript=i), expr), top=cur_top, left=left_margin + (i - 5) * 115.0)

    # Ltot := x10
    cur_top += 30.0
    add_math(make_define(make_id("L", subscript="tot"), make_id("x", is_contextual=True, subscript=10)), top=cur_top, left=left_margin)

    # Imagen del esquema de la viga
    add_text_reg(2, top_offset=30.0)
    cur_top += 25.0
    reg_img = ET.Element(tag_ws('region'), {
        'region-id': str(reg_id_counter),
        'top': f'{cur_top:.1f}',
        'left': f'{left_margin:.1f}'
    })
    ET.SubElement(reg_img, tag_ws('picture'), {
        'item-idref': 'RelImageBeam',
        'image-format': 'png',
        'display-width': '620',
        'display-height': '200'
    })
    regions_parent.append(reg_img)
    reg_id_counter += 1
    cur_top += 205.0

    # 2. Cargas Aplicadas
    add_text_reg(3, top_offset=25.0)

    # Cargas distribuidas q1 a q10
    cur_top += 25.0
    all_qs = [beam.distributed_loads.get(i, 0.0) for i in range(10)]
    for i in range(5):
        add_math(make_define(make_id("q", subscript=i+1), make_scaled(all_qs[i], beam.unit_dist_force)), top=cur_top, left=left_margin + i * 115.0)
    cur_top += 28.0
    for i in range(5, 10):
        add_math(make_define(make_id("q", subscript=i+1), make_scaled(all_qs[i], beam.unit_dist_force)), top=cur_top, left=left_margin + (i - 5) * 115.0)

    # Cargas puntuales P0 a P10
    cur_top += 30.0
    all_ps = [beam.point_loads.get(i, 0.0) for i in range(11)]
    for i in range(6):
        add_math(make_define(make_id("P", subscript=i), make_scaled(all_ps[i], beam.unit_force)), top=cur_top, left=left_margin + i * 115.0)
    cur_top += 28.0
    for i in range(6, 11):
        add_math(make_define(make_id("P", subscript=i), make_scaled(all_ps[i], beam.unit_force)), top=cur_top, left=left_margin + (i - 6) * 115.0)

    # Momentos aplicados M0 a M10
    cur_top += 30.0
    all_ms = [beam.applied_moments.get(i, 0.0) for i in range(11)]
    for i in range(6):
        add_math(make_define(make_id("M", subscript=i), make_scaled(all_ms[i], beam.unit_moment)), top=cur_top, left=left_margin + i * 115.0)
    cur_top += 28.0
    for i in range(6, 11):
        add_math(make_define(make_id("M", subscript=i), make_scaled(all_ms[i], beam.unit_moment)), top=cur_top, left=left_margin + (i - 6) * 115.0)

    # 3. Reacciones de apoyo
    add_text_reg(4, top_offset=30.0)
    reactions = beam.calculate_reactions()
    cur_top += 25.0
    val_vd = reactions.get("VD", 35.0)
    val_va = reactions.get("VA", 23.0)
    add_math(make_define(make_id("V", subscript="D"), make_scaled(val_vd, beam.unit_force)), top=cur_top, left=left_margin)
    add_math(make_define(make_id("V", subscript="A"), make_scaled(val_va, beam.unit_force)), top=cur_top, left=left_margin + 200.0)

    # 4. Funciones de Secciones M(x) y Q(x)
    add_text_reg(5, top_offset=30.0)
    cur_top += 25.0

    # M(x)
    fn_m_target = ET.Element(tag_ml('function'))
    fn_m_target.append(make_id("M"))
    bvars_m = ET.SubElement(fn_m_target, tag_ml('boundVars'))
    bvars_m.append(make_id("x"))

    m_expr = make_apply('mult', make_id("V", is_contextual=True, subscript="A"), make_id("x", is_contextual=True))
    
    # Tramo 1 distribuida activa y superada
    cond_q1_act = make_parens(make_apply('greaterThan', make_apply('greaterThan', make_id("x", is_contextual=True, subscript=1), make_id("x", is_contextual=True)), make_id("x", is_contextual=True, subscript=0)))
    term_q1_act = make_apply('mult', make_apply('mult', cond_q1_act, make_id("q", is_contextual=True, subscript=1)), make_apply('div', make_apply('pow', make_id("x", is_contextual=True), make_real(2)), make_real(2)))
    m_expr = make_apply('minus', m_expr, term_q1_act)

    cond_q1_sup = make_parens(make_apply('greaterOrEqual', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=1)))
    arm_q1_sup = make_parens(make_apply('minus', make_id("x", is_contextual=True), make_apply('div', make_id("L", is_contextual=True, subscript=1), make_real(2))))
    term_q1_sup = make_apply('mult', make_apply('mult', make_apply('mult', cond_q1_sup, make_id("q", is_contextual=True, subscript=1)), make_id("L", is_contextual=True, subscript=1)), arm_q1_sup)
    m_expr = make_apply('minus', m_expr, term_q1_sup)

    # Momento nodo 1
    cond_m1 = make_parens(make_apply('greaterOrEqual', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=1)))
    term_m1 = make_apply('mult', cond_m1, make_id("M", is_contextual=True, subscript=1))
    m_expr = make_apply('plus', m_expr, term_m1)

    # Carga puntual nodo 2
    cond_p2 = make_parens(make_apply('greaterOrEqual', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=2)))
    arm_p2 = make_parens(make_apply('minus', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=2)))
    term_p2 = make_apply('mult', make_apply('mult', cond_p2, make_id("P", is_contextual=True, subscript=2)), arm_p2)
    m_expr = make_apply('minus', m_expr, term_p2)

    # Reacción apoyo D (nodo 3)
    cond_vd = make_parens(make_apply('greaterOrEqual', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=3)))
    arm_vd = make_parens(make_apply('minus', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=3)))
    term_vd = make_apply('mult', make_apply('mult', cond_vd, make_id("V", is_contextual=True, subscript="D")), arm_vd)
    m_expr = make_apply('plus', m_expr, term_vd)

    add_math(make_define(fn_m_target, m_expr), top=cur_top, left=left_margin)

    # Q(x)
    cur_top += 55.0
    fn_q_target = ET.Element(tag_ml('function'))
    fn_q_target.append(make_id("Q"))
    bvars_q = ET.SubElement(fn_q_target, tag_ml('boundVars'))
    bvars_q.append(make_id("x"))

    q_expr = make_id("V", is_contextual=True, subscript="A")
    term_q1_act_v = make_apply('mult', make_apply('mult', cond_q1_act, make_id("q", is_contextual=True, subscript=1)), make_id("x", is_contextual=True))
    q_expr = make_apply('minus', q_expr, term_q1_act_v)

    term_q1_sup_v = make_apply('mult', make_apply('mult', cond_q1_sup, make_id("q", is_contextual=True, subscript=1)), make_id("L", is_contextual=True, subscript=1))
    q_expr = make_apply('minus', q_expr, term_q1_sup_v)

    term_p2_v = make_apply('mult', cond_p2, make_id("P", is_contextual=True, subscript=2))
    q_expr = make_apply('minus', q_expr, term_p2_v)

    term_vd_v = make_apply('mult', cond_vd, make_id("V", is_contextual=True, subscript="D"))
    q_expr = make_apply('plus', q_expr, term_vd_v)

    cond_p4 = make_parens(make_apply('greaterOrEqual', make_id("x", is_contextual=True), make_id("x", is_contextual=True, subscript=4)))
    term_p4_v = make_apply('mult', cond_p4, make_id("P", is_contextual=True, subscript=4))
    q_expr = make_apply('minus', q_expr, term_p4_v)

    add_math(make_define(fn_q_target, q_expr), top=cur_top, left=left_margin)

    # 5. Rango
    add_text_reg(6, top_offset=45.0)
    cur_top += 25.0
    def_x_range = ET.Element(tag_ml('define'))
    def_x_range.append(make_id("x"))
    range_el = ET.SubElement(def_x_range, tag_ml('range'))
    seq_el = ET.SubElement(range_el, tag_ml('sequence'))
    seq_el.append(make_scaled(0.0, beam.unit_length))
    seq_el.append(make_scaled(0.001, beam.unit_length))
    range_el.append(make_id("L", is_contextual=True, subscript="tot"))
    add_math(def_x_range, top=cur_top, left=left_margin)

    # 6. Gráficos
    add_text_reg(7, top_offset=30.0)
    cur_top += 25.0

    if plot_q_orig is not None:
        plot_q_orig.attrib['region-id'] = str(reg_id_counter)
        plot_q_orig.attrib['top'] = f'{cur_top:.1f}'
        plot_q_orig.attrib['left'] = f'{left_margin:.1f}'
        regions_parent.append(plot_q_orig)
        reg_id_counter += 1

    cur_top += 250.0
    if plot_m_orig is not None:
        plot_m_orig.attrib['region-id'] = str(reg_id_counter)
        plot_m_orig.attrib['top'] = f'{cur_top:.1f}'
        plot_m_orig.attrib['left'] = f'{left_margin:.1f}'
        regions_parent.append(plot_m_orig)
        reg_id_counter += 1

    files['mathcad/worksheet.xml'] = ET.tostring(ws_root, encoding='utf-8', xml_declaration=True)

    with zipfile.ZipFile(output_mcdx_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)

    return output_mcdx_path
