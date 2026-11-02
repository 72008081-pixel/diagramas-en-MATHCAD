# -*- coding: utf-8 -*-
import os, sys

sys.stdout.reconfigure(encoding='utf-8')

target_files = [
    r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\01. PLANTILLAS FINALES EXAMENES\03. MATHCAD\index.html",
    r"D:\ANTIGRAVITY CUBA V\01. Análisis Estructural II\AUTOMATIZACION ARMADURAS Y VIGAS\mathcad\index.html"
]

new_js_generator = """    // ==========================================
    // GENERADOR DINÁMICO NATIVO DE .MCDX EN JS (EXACTO N TRAMOS)
    // ==========================================
    async function generateMCDX() {
      const btn = document.getElementById('btnDownloadMcdx');
      const oldHtml = btn.innerHTML;
      btn.innerHTML = `<span class="animate-spin">⏳</span> Generando .mcdx...`;
      btn.disabled = true;

      try {
        // Cargar plantilla base corregida y libre de parásitos
        let resp = await fetch('./PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx');
        if (!resp.ok) {
          resp = await fetch('./PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx');
        }
        if (!resp.ok) throw new Error('No se pudo cargar la plantilla base');
        const blob = await resp.blob();

        const zip = await JSZip.loadAsync(blob);

        // Limpiar Typography.Variants de todos los archivos XML en el ZIP
        for (const fname of Object.keys(zip.files)) {
          if (fname.endsWith('.xml')) {
            let content = await zip.file(fname).async('string');
            content = content.replace(/\\s*Typography\\.[a-zA-Z0-9]+="[^"]*"/g, '');
            zip.file(fname, content);
          }
        }

        let wsXmlStr = await zip.file('mathcad/worksheet.xml').async('string');
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(wsXmlStr, 'application/xml');

        // 1. Eliminar regiones parásitas o repetidas
        const unwantedIds = new Set(['0', '1', '57', '60', '63', '65']);
        unwantedIds.forEach(id => {
          const el = xmlDoc.querySelector(`[region-id="${id}"]`);
          if (el && el.parentNode) el.parentNode.removeChild(el);
        });

        const N = state.numSpans;

        // 2. Modificar valores de longitudes L1..LN y eliminar LN+1..L10 (Regiones 2..11)
        for (let i = 0; i < 10; i++) {
          const regId = (2 + i).toString();
          const reg = xmlDoc.querySelector(`[region-id="${regId}"]`);
          if (reg) {
            if (i < N) {
              const real = reg.querySelector('real');
              if (real) real.textContent = state.spans[i].toString();
            } else {
              if (reg.parentNode) reg.parentNode.removeChild(reg);
            }
          }
        }

        // 2.5 Eliminar coordenadas nodales x_{N+1}..x_10 (Regiones 12..22)
        for (let i = 0; i <= 10; i++) {
          const regId = (12 + i).toString();
          const reg = xmlDoc.querySelector(`[region-id="${regId}"]`);
          if (reg && i > N) {
            if (reg.parentNode) reg.parentNode.removeChild(reg);
          }
        }

        // 2.6 Modificar Ltot (Region 23) para vincular a x_N
        const r23 = xmlDoc.querySelector('[region-id="23"]');
        if (r23) {
          const defEl = r23.querySelector('define');
          if (defEl && defEl.children.length >= 2) {
            defEl.replaceChild(mkId('x', N), defEl.children[1]);
          }
        }

        // 3. Modificar Cargas Distribuidas q1..qN y eliminar qN+1..q10 (Regiones 25..34)
        for (let i = 0; i < 10; i++) {
          const regId = (25 + i).toString();
          const reg = xmlDoc.querySelector(`[region-id="${regId}"]`);
          if (reg) {
            if (i < N) {
              const real = reg.querySelector('real');
              if (real) real.textContent = (state.distLoads[i] || 0).toString();
            } else {
              if (reg.parentNode) reg.parentNode.removeChild(reg);
            }
          }
        }

        // 4. Modificar Cargas Puntuales P0..PN y eliminar PN+1..P10 (Regiones 35..45)
        for (let i = 0; i <= 10; i++) {
          const regId = (35 + i).toString();
          const reg = xmlDoc.querySelector(`[region-id="${regId}"]`);
          if (reg) {
            if (i <= N) {
              const real = reg.querySelector('real');
              if (real) real.textContent = (state.pointLoads[i] || 0).toString();
            } else {
              if (reg.parentNode) reg.parentNode.removeChild(reg);
            }
          }
        }

        // 5. Modificar Momentos M0..MN y eliminar MN+1..M10 (Regiones 46..56)
        for (let i = 0; i <= 10; i++) {
          const regId = (46 + i).toString();
          const reg = xmlDoc.querySelector(`[region-id="${regId}"]`);
          if (reg) {
            if (i <= N) {
              const real = reg.querySelector('real');
              if (real) real.textContent = (state.appliedMoments[i] || 0).toString();
            } else {
              if (reg.parentNode) reg.parentNode.removeChild(reg);
            }
          }
        }

        // 6. Modificar Reacciones VA (r59) y VD (r58)
        const r58 = xmlDoc.querySelector('[region-id="58"]');
        if (r58) {
          const real = r58.querySelector('real');
          if (real) real.textContent = state.reactions.VD.toFixed(4);
        }
        const r59 = xmlDoc.querySelector('[region-id="59"]');
        if (r59) {
          const real = r59.querySelector('real');
          if (real) real.textContent = state.reactions.VA.toFixed(4);
        }

        // 7. Reorganización geométrica limpia anti-colisión
        const setPos = (rid, top, left, w, h) => {
          const el = xmlDoc.querySelector(`[region-id="${rid}"]`);
          if (el) {
            el.setAttribute('top', top.toFixed(1));
            el.setAttribute('left', left.toFixed(1));
            if (w !== undefined) el.setAttribute('width', w.toString());
            if (h !== undefined) el.setAttribute('height', h.toString());
          }
        };

        setPos('2', 35.0, 37.8);  setPos('3', 35.0, 170.0); setPos('4', 35.0, 305.0); setPos('5', 35.0, 440.0); setPos('6', 35.0, 575.0);
        setPos('7', 68.0, 37.8);  setPos('8', 68.0, 170.0); setPos('9', 68.0, 305.0); setPos('10', 68.0, 440.0); setPos('11', 68.0, 575.0);

        const coordTop = (N > 5) ? 105.0 : 72.0;
        setPos('12', coordTop, 37.8); setPos('13', coordTop, 150.0); setPos('14', coordTop, 265.0); setPos('15', coordTop, 380.0); setPos('16', coordTop, 495.0); setPos('17', coordTop, 610.0);
        setPos('18', coordTop + 35, 37.8); setPos('19', coordTop + 35, 150.0); setPos('20', coordTop + 35, 265.0); setPos('21', coordTop + 35, 380.0); setPos('22', coordTop + 35, 495.0);

        const ltotTop = coordTop + (N > 5 ? 70.0 : 38.0);
        setPos('23', ltotTop, 37.8);

        const imgTop = ltotTop + 38.0;
        const r24 = xmlDoc.querySelector('[region-id="24"]');
        if (r24) {
          r24.setAttribute('top', imgTop.toFixed(1));
          r24.setAttribute('left', '37.8');
          r24.setAttribute('width', '700');
          r24.setAttribute('height', '145');
          const png = r24.querySelector('png');
          if (png) {
            png.setAttribute('display-width', '700');
            png.setAttribute('display-height', '145');
          }
        }

        const qTop = imgTop + 160.0;
        setPos('25', qTop, 37.8);  setPos('26', qTop, 170.0); setPos('27', qTop, 305.0); setPos('28', qTop, 440.0); setPos('29', qTop, 575.0);
        setPos('30', qTop + 35, 37.8); setPos('31', qTop + 35, 170.0); setPos('32', qTop + 35, 305.0); setPos('33', qTop + 35, 440.0); setPos('34', qTop + 35, 575.0);

        const pTop = qTop + (N > 5 ? 72.0 : 38.0);
        setPos('35', pTop, 37.8);  setPos('36', pTop, 150.0); setPos('37', pTop, 265.0); setPos('38', pTop, 380.0); setPos('39', pTop, 495.0); setPos('40', pTop, 610.0);
        setPos('41', pTop + 35, 37.8); setPos('42', pTop + 35, 150.0); setPos('43', pTop + 35, 265.0); setPos('44', pTop + 35, 380.0); setPos('45', pTop + 35, 495.0);

        const mTop = pTop + (N > 5 ? 72.0 : 38.0);
        setPos('46', mTop, 37.8);  setPos('47', mTop, 205.0); setPos('48', mTop, 375.0); setPos('49', mTop, 545.0);
        setPos('50', mTop + 35, 37.8); setPos('51', mTop + 35, 205.0); setPos('52', mTop + 35, 375.0); setPos('53', mTop + 35, 545.0);
        setPos('54', mTop + 70, 37.8); setPos('55', mTop + 70, 205.0); setPos('56', mTop + 70, 375.0);

        const reacTop = mTop + (N > 3 ? 75.0 : 40.0);
        setPos('58', reacTop, 37.8);
        setPos('59', reacTop, 230.0);

        const rangeXTop = reacTop + 45.0;
        setPos('64', rangeXTop, 37.8); // x := 0 .. Ltot

        const vFuncTop = rangeXTop + 45.0;
        setPos('62', vFuncTop, 37.8); // V(x)

        const mFuncTop = vFuncTop + 65.0;
        setPos('61', mFuncTop, 37.8); // M(x)

        const dfcPlotTop = mFuncTop + 80.0;
        setPos('66', dfcPlotTop, 37.8, 680, 230); // Gráfico V(x)

        const dmfPlotTop = dfcPlotTop + 260.0;
        setPos('67', dmfPlotTop, 37.8, 680, 230); // Gráfico M(x)

        // 8. Construcción de Expresiones con intervalos exactos del docente Alain Alanoca
        const ML_NS = 'http://schemas.mathsoft.com/math50';
        const WS_NS = 'http://schemas.mathsoft.com/worksheet50';
        const P_NS = 'http://schemas.microsoft.com/winfx/2006/xaml/presentation';
        const C_NS = 'clr-namespace:Ptc.Wpf;assembly=Ptc.Core';

        function mkId(name, subscript) {
          const el = xmlDoc.createElementNS(ML_NS, 'ml:id');
          el.setAttribute('labels', 'VARIABLE');
          el.setAttribute('label-is-contextual', 'true');
          el.setAttribute('xml:space', 'preserve');
          if (subscript !== undefined && subscript !== null) {
            const span = xmlDoc.createElementNS(P_NS, 'p:Span');
            span.textContent = name;
            const sub = xmlDoc.createElementNS(C_NS, 'c:Subscript');
            sub.textContent = subscript.toString();
            span.appendChild(sub);
            el.appendChild(span);
          } else {
            el.textContent = name;
          }
          return el;
        }

        function mkReal(val) {
          const el = xmlDoc.createElementNS(ML_NS, 'ml:real');
          el.textContent = (typeof val === 'number') ? val.toString() : val;
          return el;
        }

        function mkParens(child) {
          const el = xmlDoc.createElementNS(ML_NS, 'ml:parens');
          el.appendChild(child.cloneNode(true));
          return el;
        }

        function mkApply(opName, ...args) {
          const el = xmlDoc.createElementNS(ML_NS, 'ml:apply');
          const op = xmlDoc.createElementNS(ML_NS, `ml:${opName}`);
          el.appendChild(op);
          for (const a of args) {
            el.appendChild(a.cloneNode(true));
          }
          return el;
        }

        function buildChain(terms) {
          let acc = null;
          for (const [sign, el] of terms) {
            const elClone = el.cloneNode(true);
            if (!acc) {
              if (sign === '+') acc = elClone;
              else acc = mkApply('minus', elClone);
            } else {
              const op = (sign === '+') ? 'plus' : 'minus';
              acc = mkApply(op, acc, elClone);
            }
          }
          return acc || mkReal(0);
        }

        const termsM = [];
        const termsQ = [];

        // Apoyos y Reacciones
        const supNodes = Object.keys(state.supports).map(Number).sort((a,b)=>a-b);
        let nA = 0, nB = N;
        if (supNodes.length >= 2) {
          nA = supNodes[0];
          nB = supNodes[1];
        } else if (supNodes.length === 1) {
          nA = supNodes[0];
          nB = supNodes[0];
        }

        // Reacción A
        if (nA === 0) {
          termsM.push(['+', mkApply('mult', mkId('V', 'A'), mkId('x'))]);
          termsQ.push(['+', mkId('V', 'A')]);
        } else {
          const condVA = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', nA)));
          const armVA = mkParens(mkApply('minus', mkId('x'), mkId('x', nA)));
          termsM.push(['+', mkApply('mult', mkApply('mult', condVA, mkId('V', 'A')), armVA)]);
          termsQ.push(['+', mkApply('mult', condVA, mkId('V', 'A'))]);
        }

        // Reacción B (VD) - en nodo nB real
        if (supNodes.length >= 2 && nB !== nA) {
          const condVB = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', nB)));
          const armVB = mkParens(mkApply('minus', mkId('x'), mkId('x', nB)));
          termsM.push(['+', mkApply('mult', mkApply('mult', condVB, mkId('V', 'D')), armVB)]);
          termsQ.push(['+', mkApply('mult', condVB, mkId('V', 'D'))]);
        }

        // Tramos 1..N con sintaxis exacta del docente Alain Alanoca: (x_{k-1} < x < x_k)
        for (let k = 1; k <= N; k++) {
          const condIn = mkParens(mkApply('lessThan',
            mkApply('lessThan', mkId('x', k - 1), mkId('x')),
            mkId('x', k)));
          const armDiff = mkParens(mkApply('minus', mkId('x'), mkId('x', k - 1)));
          const loadIn = mkParens(mkApply('mult', mkId('q', k), armDiff));
          const armIn = mkParens(mkApply('div', armDiff, mkReal(2)));

          const condSup = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', k)));
          const loadSup = mkParens(mkApply('mult', mkId('q', k), mkId('L', k)));
          const cgPos = mkParens(mkApply('plus', mkId('x', k - 1), mkApply('div', mkId('L', k), mkReal(2))));
          const armCg = mkParens(mkApply('minus', mkId('x'), cgPos));

          // En V(x): Intervalo primero * Carga
          termsQ.push(['-', mkApply('mult', condIn, loadIn)]);
          termsQ.push(['-', mkApply('mult', condSup, loadSup)]);

          // En M(x): Intervalo primero * Carga * Brazo explícito
          termsM.push(['-', mkApply('mult', mkApply('mult', condIn, loadIn), armIn)]);
          termsM.push(['-', mkApply('mult', mkApply('mult', condSup, loadSup), armCg)]);

          // Carga puntual P_k (solo si P_k != 0)
          const pVal = state.pointLoads[k] || 0;
          if (pVal !== 0) {
            const condPk = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', k)));
            const armPk = mkParens(mkApply('minus', mkId('x'), mkId('x', k)));
            termsQ.push(['-', mkApply('mult', condPk, mkId('P', k))]);
            termsM.push(['-', mkApply('mult', mkApply('mult', condPk, mkId('P', k)), armPk)]);
          }

          // Momento concentrado M_k (solo si M_k != 0)
          const mVal = state.appliedMoments[k] || 0;
          if (mVal !== 0) {
            const condMk = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', k)));
            termsM.push(['+', mkApply('mult', condMk, mkId('M', k))]);
          }
        }

        // Carga puntual P0 y Momento M0 en x=0 (solo si existen y son no nulos)
        const p0Val = state.pointLoads[0] || 0;
        if (p0Val !== 0) {
          const condP0 = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', 0)));
          termsQ.push(['-', mkApply('mult', condP0, mkId('P', 0))]);
          termsM.push(['-', mkApply('mult', mkApply('mult', condP0, mkId('P', 0)), mkId('x'))]);
        }
        const m0Val = state.appliedMoments[0] || 0;
        if (m0Val !== 0) {
          const condM0 = mkParens(mkApply('greaterOrEqual', mkId('x'), mkId('x', 0)));
          termsM.push(['+', mkApply('mult', condM0, mkId('M', 0))]);
        }

        // Reemplazar definición de M(x) en R61
        const r61 = xmlDoc.querySelector('[region-id="61"]');
        if (r61) {
          const defEl = r61.querySelector('define');
          if (defEl && defEl.children.length >= 2) {
            defEl.replaceChild(buildChain(termsM), defEl.children[1]);
          }
        }

        // Reemplazar definición de V(x) en R62
        const r62 = xmlDoc.querySelector('[region-id="62"]');
        if (r62) {
          const defEl = r62.querySelector('define');
          if (defEl && defEl.children.length >= 2) {
            const fnEl = defEl.querySelector('function');
            if (fnEl) {
              const fnId = fnEl.querySelector('id');
              if (fnId) fnId.textContent = 'V';
            }
            defEl.replaceChild(buildChain(termsQ), defEl.children[1]);
          }
        }

        // 9. Escalamiento dinámico de límites en Gráficos 2D
        const coords = getNodeCoords();
        const Ltot = coords[coords.length - 1];

        // 9.5 Secuencia estricta de esquema XSD para gráficos 2D (numberFormat antes de plotEquations)
        function fixAxis(ax, maxVal) {
          const nfs = ax.querySelectorAll('numberFormat');
          nfs.forEach(nf => nf.parentNode.removeChild(nf));

          const nf = xmlDoc.createElementNS(WS_NS, 'numberFormat');
          const dec = xmlDoc.createElementNS(WS_NS, 'decimal');
          dec.setAttribute('precision', '3');
          dec.setAttribute('show-trailing-zeros', 'false');
          dec.setAttribute('radix', 'dec');
          dec.setAttribute('imaginary-value', 'i');
          nf.appendChild(dec);

          const peq = ax.querySelector('plotEquations');
          if (peq) {
            ax.insertBefore(nf, peq);
          } else {
            ax.appendChild(nf);
          }

          const aline = ax.querySelector('axisLine');
          if (aline) {
            aline.setAttribute('positionticmark', Math.round(maxVal).toString());
          }
        }

        const r66 = xmlDoc.querySelector('[region-id="66"]');
        if (r66) {
          const plot = r66.querySelector('plot');
          if (plot) {
            for (const peq of plot.querySelectorAll('yAxis plotEquation id')) {
              if (peq.textContent === 'Q') peq.textContent = 'V';
            }
            const xAx = plot.querySelector('xAxis');
            if (xAx) fixAxis(xAx, Ltot);
            const yAx = plot.querySelector('yAxis');
            if (yAx) fixAxis(yAx, 0);
          }
        }

        const r67 = xmlDoc.querySelector('[region-id="67"]');
        if (r67) {
          const plot = r67.querySelector('plot');
          if (plot) {
            const xAx = plot.querySelector('xAxis');
            if (xAx) fixAxis(xAx, Ltot);
            const yAx = plot.querySelector('yAxis');
            if (yAx) fixAxis(yAx, 0);
          }
        }

        // Sanitizar todos los axisLine
        const allAxisLines = xmlDoc.querySelectorAll('axisLine');
        allAxisLines.forEach(al => {
          const ptm = al.getAttribute('positionticmark');
          if (ptm !== null && ptm !== undefined) {
            const num = parseFloat(ptm);
            al.setAttribute('positionticmark', isNaN(num) ? '0' : Math.round(num).toString());
          }
        });

        // Guardar worksheet.xml modificado
        const serializer = new XMLSerializer();
        const newXml = serializer.serializeToString(xmlDoc);
        zip.file('mathcad/worksheet.xml', newXml);

        // Actualizar Imagen Image0.png desde el canvas
        const canvas = document.getElementById('beamCanvas');
        const canvasDataUrl = canvas.toDataURL('image/png');
        const imgBase64 = canvasDataUrl.split(',')[1];
        zip.file('mathcad/media/Image0.png', imgBase64, { base64: true });

        // Empaquetar y disparar descarga
        const finalBlob = await zip.generateAsync({ type: 'blob' });
        saveAs(finalBlob, `Viga_${state.numSpans}Tramos_Mathcad_Prime_11.mcdx`);
        showToast('¡Archivo .mcdx generado y descargado con éxito!');
      } catch (err) {
        console.error(err);
        const link = document.createElement('a');
        link.href = './PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx';
        link.download = 'PLANTILLA_MAESTRA_10_TRAMOS_CORREGIDA.mcdx';
        link.click();
        showToast('Descargando plantilla maestra base');
      } finally {
        btn.innerHTML = oldHtml;
        btn.disabled = false;
      }
    }"""

start_marker = "    // ==========================================\n    // GENERADOR DINÁMICO NATIVO DE .MCDX EN JS"
end_marker = "    // ==========================================\n    // GENERADOR DE REPORTE IMPRIMIBLE"

for target in target_files:
    if not os.path.exists(target):
        print("Missing target:", target)
        continue
    with open(target, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalizar \r\n para búsqueda
    c_norm = content.replace('\r\n', '\n')
    idx_start = c_norm.find(start_marker)
    idx_end = c_norm.find(end_marker)

    if idx_start == -1 or idx_end == -1:
        print(f"Markers not found in {target}: start={idx_start}, end={idx_end}")
        continue

    new_content = c_norm[:idx_start] + new_js_generator + "\n\n" + c_norm[idx_end:]

    # Corregir renderMathcadCode para invertir desigualdades
    new_content = new_content.replace(
        "mLines.push(`- (x1 > x > x0) · q1 · (x² / 2)`);",
        "mLines.push(`- (x0 < x < x1) · q1 · (x² / 2)`);"
    )
    new_content = new_content.replace(
        "qLines.push(`- (x1 > x > x0) · q1 · x`);",
        "qLines.push(`- (x0 < x < x1) · q1 · x`);"
    )
    new_content = new_content.replace(
        "mLines.push(`- (x${i + 1} > x > x${i}) · q${i + 1} · ((x - x${i})² / 2)`);",
        "mLines.push(`- (x${i} < x < x${i + 1}) · q${i + 1} · ((x - x${i})² / 2)`);"
    )
    new_content = new_content.replace(
        "qLines.push(`- (x${i + 1} > x > x${i}) · q${i + 1} · (x - x${i})`);",
        "qLines.push(`- (x${i} < x < x${i + 1}) · q${i + 1} · (x - x${i})`);"
    )

    with open(target, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(new_content)
    print(f"✅ Successfully updated: {target}")

print("Done updating both targets!")
