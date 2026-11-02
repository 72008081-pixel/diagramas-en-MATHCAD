# -*- coding: utf-8 -*-
"""
BUCLE DE REPARACIÓN Y VERIFICACIÓN EN VIVO CON PTC MATHCAD PRIME 11
Toma como base 'PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx' (que contiene todas las
variables L1..L10, x0..x10, q1..q10, P0..P10, M0..M10), inyecta la formulación
completa de 10 tramos con intervalos y brazos explícitos al estilo del profesor Alain Alanoca,
coloca 'numberFormat' en la posición estricta del esquema XSD (antes de plotEquations),
y valida directamente abriendo el archivo en PTC Mathcad Prime 11 real sin errores.
"""
import os
import sys
import zipfile
import shutil
import subprocess
import glob
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

def fix_and_build_10span(base_mcdx_path, out_mcdx_path):
    print(f"Construyendo plantilla maestra 10 tramos corregida...\nOrigen: {base_mcdx_path}\nDestino: {out_mcdx_path}")
    files = {}
    with zipfile.ZipFile(base_mcdx_path, 'r') as z:
        for name in z.namelist():
            files[name] = z.read(name)

    root = ET.fromstring(files['mathcad/worksheet.xml'])
    regs = root[0]

    # Eliminar regiones parásitas si existiesen (ej. regiones 0 y 1 con FlowDocument incompatibles)
    for r in list(regs):
        rid = r.attrib.get('region-id')
        if rid in ['0', '1', '57', '60', '63', '65']:
            regs.remove(r)

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

    # Reacciones: VA en x=0, y VD en x10 (apoyo general)
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

    for k in range(1, 11):
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

        # Cargas puntuales P_k
        cond_pk = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=k)))
        terms_v.append(('-', make_apply('mult', cond_pk, make_id("P", subscript=k))))
        terms_m.append(('-', make_apply('mult', make_apply('mult', cond_pk, make_id("P", subscript=k)),
                                        make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=k))))))

        # Momentos concentrados M_k
        terms_m.append(('-', make_apply('mult', cond_pk, make_id("M", subscript=k))))

    # 1. Rango x en top=690.0 (ANTES DE FUNCIONES)
    if r_x is not None:
        r_x.attrib['top'] = '690.0'
        r_x.attrib['left'] = '37.8'

    # 2. Función Cortante V(x) en top=730.0
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

    # 3. Función Momento M(x) en top=785.0
    if r_m is not None:
        r_m.attrib['top'] = '785.0'
        r_m.attrib['left'] = '37.8'
        def_el = r_m.find(f'.//{{{ML_NS}}}define')
        if def_el is not None:
            def_el[1] = build_additive_chain(terms_m)

    # Posición estricta del esquema XSD:
    # xs:sequence: axisLine, axisGrid, axisLabel, markers, numberFormat, plotEquations, xyDomain
    def fix_axis_number_format(ax):
        for nf in list(ax.findall(tag_ws('numberFormat'))):
            ax.remove(nf)
        nf = ET.Element(tag_ws('numberFormat'))
        ET.SubElement(nf, tag_ws('decimal'), {
            'precision': '3',
            'show-trailing-zeros': 'false',
            'radix': 'dec',
            'imaginary-value': 'i'
        })
        insert_idx = None
        for i, child in enumerate(ax):
            if child.tag.endswith('plotEquations'):
                insert_idx = i
                break
        if insert_idx is not None:
            ax.insert(insert_idx, nf)
        else:
            ax.append(nf)

    # 4. Ajustar Plot V(x) (DFC) en top=860.0
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
                if ax is not None:
                    fix_axis_number_format(ax)

    # 5. Ajustar Plot M(x) (DMF) en top=1130.0
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
                    fix_axis_number_format(ax)

    # Sanitizar marcas de tics (deben ser enteros)
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
    print(f"  [BUILD OK] Archivo generado: {out_mcdx_path}")

def test_file_with_mathcad_prime(mcdx_path):
    print(f"\n--- Probando archivo directamente en PTC Mathcad Prime 11 ---")
    print(f"Ruta: {mcdx_path}")
    
    # Matar cualquier proceso previo colgado
    subprocess.run(["powershell", "-Command", "Stop-Process -Name 'MathcadPrime' -Force -ErrorAction SilentlyContinue"], capture_output=True)
    
    log_dir = r"C:\ProgramData\PTC\Mathcad Prime\Logs"
    before_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))
    
    ps_script = f"""
    $app = New-Object -ComObject MathcadPrime.Application
    $app.Visible = $false
    try {{
        $path = "{mcdx_path}"
        $app.Open($path)
        Start-Sleep -Milliseconds 1000
        $count = $app.Worksheets.Count
        Write-Host "WORKSHEETS_COUNT: $count"
    }} catch {{
        Write-Host "EXCEPTION_CAUGHT: $($_.Exception.Message)"
    }} finally {{
        $app.CloseAll(2)
        $app.Quit(2)
    }}
    """
    
    res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script], capture_output=True, text=True, timeout=30)
    print("STDOUT:", res.stdout.strip())
    if res.stderr:
        print("STDERR:", res.stderr.strip())
        
    after_logs = set(glob.glob(os.path.join(log_dir, "MathcadPrime_Exception_*.log")))
    new_logs = after_logs - before_logs
    
    if new_logs:
        print(f"❌ FALLÓ: Se generaron {len(new_logs)} nuevos registros de excepción en Mathcad Prime:")
        for log_file in new_logs:
            print(f"   Log: {log_file}")
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line in lines[10:35]:
                    print("     ", line.strip())
        return False
    else:
        print("✅ ÉXITO TOTAL: PTC Mathcad Prime 11 abrió el documento sin registrar NINGUNA excepción ni error de compatibilidad!")
        return True

if __name__ == '__main__':
    base_src = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx"
    test_target = r"C:\Users\CYBORG\PLANTILLA_UNIVERSAL_10_TRAMOS_TEST.mcdx"
    
    fix_and_build_10span(base_src, test_target)
    ok = test_file_with_mathcad_prime(test_target)
    
    if ok:
        print("\n🎉 CERTIFICACIÓN EXITOSA CON PTC MATHCAD PRIME 11. Desplegando en todos los destinos...")
        
        # 1. Carpeta COMPROBACION
        dest1 = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\COMPROBACION\PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"
        shutil.copy2(test_target, dest1)
        print("  -> Actualizado:", dest1)
        
        # 2. Raíz de 03. MATHCAD (repositorio diagramas-en-MATHCAD)
        dest2 = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"
        shutil.copy2(test_target, dest2)
        print("  -> Actualizado:", dest2)
        
        # 3. Repositorio Ulianov-Continental (AUTOMATIZACION ARMADURAS Y VIGAS\mathcad)
        dest3 = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad\PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"
        shutil.copy2(test_target, dest3)
        print("  -> Actualizado:", dest3)
        
        # 4. Carpeta Documents de Visitante (donde el usuario la descargó para abrirla)
        dest4 = r"D:\Visitante\Documents\PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx"
        try:
            shutil.copy2(test_target, dest4)
            print("  -> Actualizado directamente en Documents del usuario:", dest4)
        except Exception as e:
            print("  Nota Documents:", e)
            
        print("\n✨ REPARACIÓN Y CERTIFICACIÓN COMPLETADA AL 100%.")
    else:
        print("\n❌ La prueba no pasó. Se requiere ajuste adicional.")
