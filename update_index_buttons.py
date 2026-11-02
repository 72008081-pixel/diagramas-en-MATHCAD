# -*- coding: utf-8 -*-
import sys

def update_html(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Header Button
    target1 = '''      <button onclick="generateMCDX()" id="btnDownloadMcdx" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-gradient-to-r from-teal-500 to-sky-500 hover:from-teal-400 hover:to-sky-400 text-slate-950 flex items-center gap-1.5 shadow-md transition transform active:scale-95">
        💾 Descargar .mcdx
      </button>'''
    
    repl1 = '''      <button onclick="generateMCDX()" id="btnDownloadMcdx" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-gradient-to-r from-teal-500 to-sky-500 hover:from-teal-400 hover:to-sky-400 text-slate-950 flex items-center gap-1.5 shadow-md transition transform active:scale-95">
        💾 Descargar .mcdx
      </button>
      <a href="./PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx" download id="btnDownloadNuevaPlantilla" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 flex items-center gap-1.5 shadow-md transition transform active:scale-95">
        📥 Descargar nueva plantilla
      </a>'''

    # 2. Update Direct Downloads Bar
    target2 = '''          <a href="./PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx" download class="px-2.5 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 transition">
            📥 Plantilla Maestra 10 Tramos (.mcdx)
          </a>'''

    repl2 = '''          <a href="./PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx" download class="px-2.5 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-700 transition">
            📥 Plantilla Maestra 10 Tramos (.mcdx)
          </a>
          <a href="./PLANTILLA_UNIVERSAL_10_TRAMOS_DESDE_CERO.mcdx" download class="px-2.5 py-1 text-xs rounded bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/60 font-semibold transition flex items-center gap-1 shadow-sm">
            📥 Descargar nueva plantilla
          </a>'''

    # Normalise CRLF for target match
    content_norm = content.replace('\r\n', '\n')
    target1_norm = target1.replace('\r\n', '\n')
    target2_norm = target2.replace('\r\n', '\n')
    repl1_norm = repl1.replace('\r\n', '\n')
    repl2_norm = repl2.replace('\r\n', '\n')

    if target1_norm not in content_norm:
        print('Error: Target 1 not found in', path)
        return False
    if target2_norm not in content_norm:
        print('Error: Target 2 not found in', path)
        return False

    content_norm = content_norm.replace(target1_norm, repl1_norm, 1)
    content_norm = content_norm.replace(target2_norm, repl2_norm, 1)

    content_final = content_norm.replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content_final)

    print('Updated successfully:', path)
    return True

p1 = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\index.html"
p2 = r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad\index.html"
update_html(p1)
update_html(p2)
