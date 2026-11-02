# -*- coding: utf-8 -*-
import sys

def patch_file(path):
    print(f"Patching {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update default beam to Viga 2 parameters (5m, 4m, 1m, q2=700)
    old_beam = """        b = BeamModel()
        b.spans = [2.0, 4.0, 2.0]
        b.supports = {0: 'pin', 3: 'roller'}
        b.distributed_loads = {1: 500.0} # tramo 2: q2 = 500 kg/m"""

    new_beam = """        b = BeamModel()
        b.spans = [5.0, 4.0, 1.0]
        b.supports = {0: 'pin', 3: 'roller'}
        b.distributed_loads = {1: 700.0} # tramo 2: q2 = 700 kg/m (Viga 2)"""

    if old_beam in content:
        content = content.replace(old_beam, new_beam)
        print("  [OK] Default beam model updated to Viga 2 parameters.")

    # Update layout positions
    old_layout = """    # -------------------------------------------------------------
    # SECCIÓN 4: ECUACIONES M(x) Y Q(x) (top: 695 a 790)
    # -------------------------------------------------------------
    set_pos('61', 695.0, 37.8)  # M(x)
    set_pos('62', 760.0, 37.8)  # Q(x)
    set_pos('64', 820.0, 37.8)  # x := 0..

    # -------------------------------------------------------------
    # SECCIÓN 5: DIAGRAMAS DFC Y DMF (top: 865 a 1400)
    # -------------------------------------------------------------
    set_pos('66', 865.0, 37.8, w=650, h=230)   # Plot Q(x) DFC
    set_pos('67', 1135.0, 37.8, w=650, h=230)  # Plot M(x) DMF"""

    new_layout = """    # -------------------------------------------------------------
    # SECCIÓN 4: ECUACIONES V(x) Y M(x) ESTILO VIGA 2 (top: 690 a 820)
    # -------------------------------------------------------------
    set_pos('64', 690.0, 37.8)  # x := 0, 0.01 .. Ltot (DEFINIDO PRIMERO)
    set_pos('62', 730.0, 37.8)  # V(x) (Cortante definido segundo)
    set_pos('61', 785.0, 37.8)  # M(x) (Momento definido tercero)

    # -------------------------------------------------------------
    # SECCIÓN 5: DIAGRAMAS DFC Y DMF (top: 860 a 1400)
    # -------------------------------------------------------------
    set_pos('66', 860.0, 37.8, w=650, h=230)   # Plot V(x) DFC
    set_pos('67', 1130.0, 37.8, w=650, h=230)  # Plot M(x) DMF"""

    if old_layout in content:
        content = content.replace(old_layout, new_layout)
        print("  [OK] Layout positions updated to Viga 2 style.")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {path}\n")

if __name__ == '__main__':
    patch_file(r'D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\fix_viga_3tramos.py')
    patch_file(r'D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad\fix_viga_3tramos.py')
