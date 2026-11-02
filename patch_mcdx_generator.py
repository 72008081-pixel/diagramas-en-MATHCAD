# -*- coding: utf-8 -*-
import sys

def patch_file(path):
    print(f"Patching {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update cond_act to lessThan chained
    old_cond = """            cond_act = make_parens(make_apply('greaterThan',
                make_apply('greaterThan', make_id("x", subscript=k+1), make_id("x")),
                make_id("x", subscript=k)))"""
    
    new_cond = """            cond_act = make_parens(make_apply('lessThan',
                make_apply('lessThan', make_id("x", subscript=k), make_id("x")),
                make_id("x", subscript=k+1)))"""

    if old_cond in content:
        content = content.replace(old_cond, new_cond)
        print("  [OK] cond_act patched to lessThan chained.")
    else:
        print("  [SKIP/ALREADY] cond_act pattern not found.")

    # 2. Update load_in and arm_in
    old_arm = """            if k == 0:
                arm_sq = make_apply('div', make_apply('pow', make_id("x"), make_real(2)), make_real(2))
                arm_v = make_id("x")
            else:
                arm_diff = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=k)))
                arm_sq = make_apply('div', make_apply('pow', arm_diff, make_real(2)), make_real(2))
                arm_v = arm_diff
                
            term_m_act = make_apply('mult', make_apply('mult', cond_act, make_id("q", subscript=k+1)), arm_sq)
            term_q_act = make_apply('mult', make_apply('mult', cond_act, make_id("q", subscript=k+1)), arm_v)
            terms_m.append(('-', term_m_act))
            terms_q.append(('-', term_q_act))"""

    new_arm = """            if k == 0:
                arm_diff = make_id("x")
                arm_in = make_parens(make_apply('div', make_id("x"), make_real(2)))
                load_in = make_parens(make_apply('mult', make_id("q", subscript=1), make_id("x")))
            else:
                arm_diff = make_parens(make_apply('minus', make_id("x"), make_id("x", subscript=k)))
                arm_in = make_parens(make_apply('div', arm_diff, make_real(2)))
                load_in = make_parens(make_apply('mult', make_id("q", subscript=k+1), arm_diff))
                
            term_q_act = make_apply('mult', cond_act, load_in)
            term_m_act = make_apply('mult', make_apply('mult', cond_act, load_in), arm_in)
            terms_q.append(('-', term_q_act))
            terms_m.append(('-', term_m_act))"""

    if old_arm in content:
        content = content.replace(old_arm, new_arm)
        print("  [OK] in-span load and arm patched to Viga 2 style.")
    else:
        print("  [SKIP/ALREADY] in-span arm pattern not found.")

    # 3. Update out-of-span terms
    old_sup = """            # Condición de tramo superado: x >= x_(k+1)
            cond_sup = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=k+1)))
            if k == 0:
                arm_cg = make_parens(make_apply('minus', make_id("x"), make_apply('div', make_id("L", subscript=1), make_real(2))))
            else:
                cg_pos = make_parens(make_apply('plus', make_id("x", subscript=k), make_apply('div', make_id("L", subscript=k+1), make_real(2))))
                arm_cg = make_parens(make_apply('minus', make_id("x"), cg_pos))
                
            term_m_sup = make_apply('mult', make_apply('mult', make_apply('mult', cond_sup, make_id("q", subscript=k+1)), make_id("L", subscript=k+1)), arm_cg)
            term_q_sup = make_apply('mult', make_apply('mult', cond_sup, make_id("q", subscript=k+1)), make_id("L", subscript=k+1))
            terms_m.append(('-', term_m_sup))
            terms_q.append(('-', term_q_sup))"""

    new_sup = """            # Condición de tramo superado: x >= x_(k+1) (Intervalo primero)
            cond_sup = make_parens(make_apply('greaterOrEqual', make_id("x"), make_id("x", subscript=k+1)))
            load_tot = make_parens(make_apply('mult', make_id("q", subscript=k+1), make_id("L", subscript=k+1)))
            if k == 0:
                cg_pos = make_parens(make_apply('div', make_id("L", subscript=1), make_real(2)))
                arm_cg = make_parens(make_apply('minus', make_id("x"), cg_pos))
            else:
                cg_pos = make_parens(make_apply('plus', make_id("x", subscript=k), make_apply('div', make_id("L", subscript=k+1), make_real(2))))
                arm_cg = make_parens(make_apply('minus', make_id("x"), cg_pos))
                
            term_q_sup = make_apply('mult', cond_sup, load_tot)
            term_m_sup = make_apply('mult', make_apply('mult', cond_sup, load_tot), arm_cg)
            terms_q.append(('-', term_q_sup))
            terms_m.append(('-', term_m_sup))"""

    if old_sup in content:
        content = content.replace(old_sup, new_sup)
        print("  [OK] out-of-span patched to Viga 2 style.")
    else:
        print("  [SKIP/ALREADY] out-of-span pattern not found.")

    # 4. Update function name Q to V in Region 62
    old_r62 = """    # Reemplazar definición de Q(x) en Región 62
    if '62' in regs_dict:
        reg_62_math = regs_dict['62'].find(tag_ws('math'))
        if reg_62_math is not None:
            reg_62_def = reg_62_math.find(tag_ml('define'))
            if reg_62_def is not None:
                reg_62_def[1] = build_additive_chain(terms_q)"""

    new_r62 = """    # Reemplazar definición de V(x) en Región 62
    if '62' in regs_dict:
        reg_62_math = regs_dict['62'].find(tag_ws('math'))
        if reg_62_math is not None:
            reg_62_def = reg_62_math.find(tag_ml('define'))
            if reg_62_def is not None:
                fn_el = reg_62_def.find(tag_ml('function'))
                if fn_el is not None:
                    fn_id = fn_el.find(tag_ml('id'))
                    if fn_id is not None:
                        fn_id.text = 'V'
                reg_62_def[1] = build_additive_chain(terms_q)"""

    if old_r62 in content:
        content = content.replace(old_r62, new_r62)
        print("  [OK] Region 62 func name set to V.")
    else:
        print("  [SKIP/ALREADY] Region 62 pattern not found.")

    # 5. Update Plot 66 equation Q to V and numberFormat
    old_p66 = """    # Actualizar Ejes en Gráfico Q(x) (Región 66)
    if '66' in regs_dict:
        p66 = regs_dict['66'].find(tag_ws('plot'))
        if p66 is not None:
            x_ax = p66.find(f".//{tag_ws('xAxis')}")
            if x_ax is not None:
                x_ax.attrib['start'] = "0"
                x_ax.attrib['end'] = f"{total_l:g}"
                aline = x_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = str(int(round(total_l)))
            y_ax = p66.find(f".//{tag_ws('yAxis')}")
            if y_ax is not None:
                y_ax.attrib['start'] = f"{q_lim_min:.1f}"
                y_ax.attrib['end'] = f"{q_lim_max:.1f}"
                aline = y_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = "0" """

    new_p66 = """    # Actualizar Ejes en Gráfico V(x) (Región 66)
    if '66' in regs_dict:
        p66 = regs_dict['66'].find(tag_ws('plot'))
        if p66 is not None:
            x_ax = p66.find(f".//{tag_ws('xAxis')}")
            if x_ax is not None:
                x_ax.attrib['start'] = "0"
                x_ax.attrib['end'] = f"{total_l:g}"
                aline = x_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = str(int(round(total_l)))
                if x_ax.find(tag_ws('numberFormat')) is None:
                    nf = ET.SubElement(x_ax, tag_ws('numberFormat'))
                    ET.SubElement(nf, tag_ws('decimal'), {'precision': '3', 'show-trailing-zeros': 'false', 'radix': 'dec', 'imaginary-value': 'i'})
            y_ax = p66.find(f".//{tag_ws('yAxis')}")
            if y_ax is not None:
                y_ax.attrib['start'] = f"{q_lim_min:.1f}"
                y_ax.attrib['end'] = f"{q_lim_max:.1f}"
                aline = y_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = "0"
                for peq in y_ax.findall(f".//{tag_ws('plotEquation')}"):
                    for el in peq.findall(f".//{tag_ml('id')}"):
                        if el.text == 'Q': el.text = 'V'
                if y_ax.find(tag_ws('numberFormat')) is None:
                    nf = ET.SubElement(y_ax, tag_ws('numberFormat'))
                    ET.SubElement(nf, tag_ws('decimal'), {'precision': '3', 'show-trailing-zeros': 'false', 'radix': 'dec', 'imaginary-value': 'i'})"""

    # Try replacement with strip
    if old_p66.strip() in content:
        content = content.replace(old_p66.strip(), new_p66.strip())
        print("  [OK] Plot 66 updated with V(x) and numberFormat.")
    else:
        # Check without trailing space
        old_p66_alt = old_p66.rstrip()
        if old_p66_alt in content:
            content = content.replace(old_p66_alt, new_p66)
            print("  [OK] Plot 66 alt updated with V(x) and numberFormat.")

    # 6. Update Plot 67 numberFormat
    old_p67 = """    # Actualizar Ejes en Gráfico M(x) (Región 67)
    if '67' in regs_dict:
        p67 = regs_dict['67'].find(tag_ws('plot'))
        if p67 is not None:
            x_ax = p67.find(f".//{tag_ws('xAxis')}")
            if x_ax is not None:
                x_ax.attrib['start'] = "0"
                x_ax.attrib['end'] = f"{total_l:g}"
                aline = x_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = str(int(round(total_l)))
            y_ax = p67.find(f".//{tag_ws('yAxis')}")
            if y_ax is not None:
                y_ax.attrib['start'] = f"{m_lim_min:.1f}"
                y_ax.attrib['end'] = f"{m_lim_max:.1f}"
                aline = y_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = "0" """

    new_p67 = """    # Actualizar Ejes en Gráfico M(x) (Región 67)
    if '67' in regs_dict:
        p67 = regs_dict['67'].find(tag_ws('plot'))
        if p67 is not None:
            x_ax = p67.find(f".//{tag_ws('xAxis')}")
            if x_ax is not None:
                x_ax.attrib['start'] = "0"
                x_ax.attrib['end'] = f"{total_l:g}"
                aline = x_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = str(int(round(total_l)))
                if x_ax.find(tag_ws('numberFormat')) is None:
                    nf = ET.SubElement(x_ax, tag_ws('numberFormat'))
                    ET.SubElement(nf, tag_ws('decimal'), {'precision': '3', 'show-trailing-zeros': 'false', 'radix': 'dec', 'imaginary-value': 'i'})
            y_ax = p67.find(f".//{tag_ws('yAxis')}")
            if y_ax is not None:
                y_ax.attrib['start'] = f"{m_lim_min:.1f}"
                y_ax.attrib['end'] = f"{m_lim_max:.1f}"
                aline = y_ax.find(tag_ws('axisLine'))
                if aline is not None:
                    aline.attrib['positionticmark'] = "0"
                if y_ax.find(tag_ws('numberFormat')) is None:
                    nf = ET.SubElement(y_ax, tag_ws('numberFormat'))
                    ET.SubElement(nf, tag_ws('decimal'), {'precision': '3', 'show-trailing-zeros': 'false', 'radix': 'dec', 'imaginary-value': 'i'})"""

    if old_p67.strip() in content:
        content = content.replace(old_p67.strip(), new_p67.strip())
        print("  [OK] Plot 67 updated with numberFormat.")
    else:
        old_p67_alt = old_p67.rstrip()
        if old_p67_alt in content:
            content = content.replace(old_p67_alt, new_p67)
            print("  [OK] Plot 67 alt updated with numberFormat.")

    # 7. Update layout order
    old_layout = """    # Ecuaciones M(x), Q(x) y Rango
    set_pos('61', 695.0, 37.8)
    set_pos('62', 760.0, 37.8)
    set_pos('64', 820.0, 37.8)

    # Diagramas DFC y DMF
    set_pos('66', 865.0, 37.8, w=650, h=230)
    set_pos('67', 1135.0, 37.8, w=650, h=230)"""

    new_layout = """    # Ecuaciones Viga 2 Estilo: Rango primero, luego V(x), luego M(x)
    set_pos('64', 690.0, 37.8)  # x := 0, 0.01 .. Ltot
    set_pos('62', 730.0, 37.8)  # V(x)
    set_pos('61', 785.0, 37.8)  # M(x)

    # Diagramas DFC y DMF
    set_pos('66', 860.0, 37.8, w=650, h=230)  # V(x) vs x
    set_pos('67', 1130.0, 37.8, w=650, h=230)  # M(x) vs x"""

    if old_layout in content:
        content = content.replace(old_layout, new_layout)
        print("  [OK] Layout order updated.")
    else:
        print("  [SKIP/ALREADY] Layout order pattern not found.")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {path}\n")

if __name__ == '__main__':
    patch_file(r'D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\mcdx_generator.py')
    patch_file(r'D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad\mcdx_generator.py')
