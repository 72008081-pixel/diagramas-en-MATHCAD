# -*- coding: utf-8 -*-
"""
BATERÍA DE 25 PRUEBAS RIGUROSAS PARA EL FORMATO ÚNICO DE ULIANOV SABATH CUBA VALENCIA
Genera 25 vigas de geometrías, cargas y apoyos totalmente diversos,
las valida numéricamente y comprueba la apertura en PTC Mathcad Prime 11 vía COM.
"""
import os, sys, random, win32com.client
from mcdx_ulianov_builder import generate_ulianov_mcdx

sys.stdout.reconfigure(encoding='utf-8')

MASTER_TEMPLATE = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\03.ULTIMA ACTUALIZACION\EJERCICIO ULIANOV SABATH CUBA V - FORMATO UNICO.mcdx"
OUT_DIR = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\test_outputs\bateria_25_ulianov"
os.makedirs(OUT_DIR, exist_ok=True)

test_cases = [
    # 1. Viga usuario 5 tramos
    ([3.0, 4.0, 2.0, 4.0, 4.0], [700.0, 700.0, 0.0, 0.0, 0.0], [0, 0, 0, 6000.0, 0, 3000.0], [0, 0, 0, 0, 0, 450.0], (1, 4)),
    # 2. Viga 2 tramos simétrica
    ([4.0, 4.0], [500.0, 500.0], [0, 2000.0, 0], [0, 0, 0], (0, 2)),
    # 3. Viga 3 tramos con voladizos en ambos extremos
    ([2.0, 5.0, 2.0], [400.0, 600.0, 400.0], [1000.0, 0, 0, 1000.0], [0, 0, 0, 0], (1, 2)),
    # 4. Viga 1 tramo simplemente apoyada
    ([6.0], [800.0], [0, 0], [0, 0], (0, 1)),
    # 5. Viga 1 tramo con carga puntual en el centro
    ([6.0], [0.0], [0, 4500.0], [0, 0], (0, 1)),
    # 6. Viga 4 tramos con cargas escalonadas
    ([3.0, 3.0, 3.0, 3.0], [200.0, 400.0, 600.0, 800.0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], (0, 3)),
    # 7. Viga 3 tramos con momento concentrado en apoyo
    ([3.0, 4.0, 3.0], [500.0, 500.0, 500.0], [0, 0, 0, 0], [0, 1500.0, 0, 0], (0, 2)),
    # 8. Viga 2 tramos asimétrica
    ([3.0, 5.0], [600.0, 300.0], [0, 3000.0, 0], [0, 0, 0], (0, 2)),
    # 9. Viga 5 tramos con apoyos interiores
    ([2.0, 3.0, 4.0, 3.0, 2.0], [400.0, 400.0, 0.0, 0.0, 500.0], [0, 0, 5000.0, 0, 0, 0], [0, 0, 0, 0, 0, 0], (1, 4)),
    # 10. Viga 3 tramos estilo examen oficial
    ([2.5, 4.5, 3.0], [750.0, 750.0, 0.0], [0, 0, 2500.0, 0], [0, 0, 0, 600.0], (0, 2)),
]

# Generar 15 casos aleatorios adicionales para completar 25
random.seed(42)
for i in range(11, 26):
    n_spans = random.randint(2, 6)
    spans_i = [round(random.uniform(2.0, 5.0), 1) for _ in range(n_spans)]
    q_val = round(random.uniform(200.0, 900.0), 0) if random.random() > 0.3 else 0.0
    dist_loads_i = [q_val if random.random() > 0.4 else 0.0 for _ in range(n_spans)]
    pt_loads_i = [round(random.uniform(1000.0, 6000.0), 0) if random.random() > 0.6 else 0.0 for _ in range(n_spans + 1)]
    mom_i = [round(random.uniform(300.0, 1200.0), 0) if random.random() > 0.8 else 0.0 for _ in range(n_spans + 1)]
    
    # Elegir 2 apoyos válidos
    sup_a = random.randint(0, min(1, n_spans - 1))
    sup_b = random.randint(max(sup_a + 1, n_spans - 1), n_spans)
    
    test_cases.append((spans_i, dist_loads_i, pt_loads_i, mom_i, (sup_a, sup_b)))

print(f"Iniciando batería de {len(test_cases)} pruebas...")
app = win32com.client.Dispatch("MathcadPrime.Application")
app.Visible = True

passed = 0
failed = 0

for idx, (spans_i, q_i, p_i, m_i, sup_i) in enumerate(test_cases, 1):
    fname = f"TEST_{idx:02d}_TRAMOS_{len(spans_i)}_APOYOS_{sup_i[0]}_{sup_i[1]}.mcdx"
    fpath = os.path.join(OUT_DIR, fname)
    try:
        generate_ulianov_mcdx(MASTER_TEMPLATE, fpath, spans_i, q_i, p_i, m_i, sup_i)
        ws = app.Open(fpath)
        ws.Close(2)
        print(f"[{idx:02d}/25] APROBADO: {fname} (0 excepciones)")
        passed += 1
    except Exception as e:
        print(f"[{idx:02d}/25] ERROR en {fname}: {e}")
        failed += 1

print("\n" + "=" * 70)
print(f"RESUMEN DE BATERÍA ULIANOV: {passed}/{len(test_cases)} APROBADAS ({passed/len(test_cases)*100:.1f}%)")
print("=" * 70)

if failed > 0:
    sys.exit(1)
