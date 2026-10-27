# Diagramas en Mathcad — Generador Automatizado para PTC Mathcad Prime 11

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Mathcad](https://img.shields.io/badge/PTC%20Mathcad-Prime%2011.0.0-orange?logo=mathcad&logoColor=white)](https://www.mathcad.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-72008081--pixel-purple?logo=github)](https://github.com/72008081-pixel)

Suite de escritorio interactiva y generador de memorias de cálculo para el análisis de vigas isostáticas e hiperestáticas en **PTC Mathcad Prime 11.0.0**. Implementa el método de **Funciones de Singularidad / Macaulay mediante operadores booleanos** para producir automáticamente las funciones seccionales, el cálculo de reacciones y los diagramas en vivo de **Fuerza Cortante (DFC)** y **Momento Flector (DMF)**.

---

## 🌟 Características Principales

1. **Interfaz Gráfica de Escritorio Intuitiva (Desktop GUI):**
   - **Barra de Presets Rápidos (1 clic):** Carga instantáneamente configuraciones de examen comunes (Ejercicio Oficial, Carga Puntual Céntrica, Carga Distribuida Uniforme, Cantilever/Empotramiento, Doble Voladizo y Viga Completa de 10 Tramos).
   - Panel de control intuitivo con pestañas dedicadas para **Tramos ($L_1 \dots L_{10}$)**, **Apoyos (Fijo, Móvil, Empotramiento)**, **Cargas Distribuidas ($q$)**, **Cargas Puntuales ($P$)** y **Momentos Concentrados ($M$)**.
   - Selector dinámico de 1 a 10 tramos con cálculo automático de coordenadas nodales ($x_0, x_1, \dots, x_n$) y longitud total $L_{\text{tot}}$.
2. **Previsualizador Vectorial en Tiempo Real (Canvas 2D):**
   - Dibuja la viga a escala proporcional mientras el usuario escribe o cambia los datos.
   - Muestra cotas de longitud por tramo y cota total.
   - Símbolos normalizados de apoyos con achurado de tierra.
   - Bloques sombreados con flechas continuas para cargas distribuidas.
   - Flechas verticales para cargas concentradas y flechas curvas para momentos aplicados.
   - **Líneas de corte de sección punteadas con etiquetas formales (`Corte 1-1`, `Corte 2-2`, etc.)** tal como se exige en evaluaciones académicas.
3. **Generación Nativa de Archivos `.mcdx`:**
   - Construye archivos nativos comprimidos en estándar OPC ZIP compatibles al 100% con **PTC Mathcad Prime 11.0.0**.
   - Incrusta automáticamente el esquema visual de la viga y sus cortes dentro de la hoja de cálculo.
   - Escribe las ecuaciones analíticas de $M(x)$ y $Q(x)$ usando la sintaxis booleana de Mathcad.
   - Configura el muestreo continuo con paso milimétrico: `x := 0 m, 0.001 m .. Ltot`.
   - Incorpora gráficos bidimensionales XY dinámicos que se actualizan en vivo.
4. **Automatización COM con Mathcad Prime:**
   - Sincronización en segundo plano con el motor oficial de Mathcad para calcular los Solve Blocks y poblar los gráficos.
   - Apertura con 1 solo clic en la interfaz gráfica de usuario de Mathcad Prime.
   - Exportación directa a PDF vectorial de alta resolución (~450-510 KB) sin necesidad de manipular Mathcad manualmente.

---

## 📊 Batería de Pruebas de Estrés: 10 Casos Reales Verificados

Se diseñó e implementó un script de verificación automatizado (`run_10_tests.py`) que conecta directamente vía COM con `MathcadPrime.Application`, genera los archivos `.mcdx`, los abre en el motor nativo de Mathcad Prime 11, sincroniza el cálculo, verifica la ausencia total de regiones corruptas y exporta a PDF vectorial:

| Caso | Nombre del Test | Configuración Estructural | Estado en Mathcad Prime 11 | Tiempo | PDF Generado | CorruptedRegion |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **01** | `TEST_01_4TRAMOS` | 4 tramos (Caso Oficial Examen: $q_1=15, P_1=20, P_2=8, M_1=10$) | **✓ APROBADO** | 4.66 s | 465.3 KB | **False (0 errores)** |
| **02** | `TEST_02_2TRAMOS` | 2 tramos, puntual central ($P=50\text{ kg}$) | **✓ APROBADO** | 4.86 s | 463.9 KB | **False (0 errores)** |
| **03** | `TEST_03_3TRAMOS` | 3 tramos, carga distribuida total ($q=10\text{ kg/m}$) | **✓ APROBADO** | 6.07 s | 484.5 KB | **False (0 errores)** |
| **04** | `TEST_04_2TRAMOS` | Voladizo cantilever empotrado en origen ($q=12, P=40$) | **✓ APROBADO** | 5.47 s | 431.9 KB | **False (0 errores)** |
| **05** | `TEST_05_4TRAMOS` | 4 tramos, doble voladizo con apoyos interiores | **✓ APROBADO** | 3.90 s | 498.9 KB | **False (0 errores)** |
| **06** | `TEST_06_3TRAMOS` | 3 tramos, momentos concentrados puros ($+30, -15\text{ kg}\cdot\text{m}$) | **✓ APROBADO** | 4.43 s | 469.3 KB | **False (0 errores)** |
| **07** | `TEST_07_5TRAMOS` | 5 tramos asimétrica con cargas combinadas ($q, P, M$) | **✓ APROBADO** | 5.16 s | 479.8 KB | **False (0 errores)** |
| **08** | `TEST_08_6TRAMOS` | 6 tramos con apoyos interiores y cargas múltiples | **✓ APROBADO** | 4.82 s | 476.1 KB | **False (0 errores)** |
| **09** | `TEST_09_8TRAMOS` | 8 tramos con cargas distribuidas y puntuales combinadas | **✓ APROBADO** | 6.63 s | 491.9 KB | **False (0 errores)** |
| **10** | `TEST_10_10TRAMOS` | **10 tramos completos** con máxima variabilidad de cargas | **✓ APROBADO** | 6.32 s | 514.7 KB | **False (0 errores)** |

> **Resultado:** 10 de 10 pruebas exitosas (100% de efectividad).

---

## 🛠️ Registro de Parches y Correcciones Realizadas

Durante las pruebas exhaustivas en el entorno real con Mathcad Prime 11, se identificaron y resolvieron los siguientes detalles técnicos:

### 1. Parche COM #1: Gestión de Procesos y Selección de Hoja Activa
- **Diagnóstico:** Mathcad Prime inicia en modo headless con una hoja en blanco por defecto (`Item(0): "Sin título"`). Al llamar a `mc.Open(path)`, el conteo de hojas asciende a 2, pero `mc.ActiveWorksheet` continuaba apuntando a la hoja vacía (generando PDFs de 1.7 KB). Adicionalmente, los procesos COM quedaban huérfanos al cerrarse la sesión.
- **Solución implementada:** Se actualizó la selección explícita del documento abierto mediante `ws = mc.Worksheets.Item(mc.Worksheets.Count - 1)`. En el bloque `finally:`, se invocan obligatoriamente `mc.CloseAll(0)` y `mc.Quit(0)` para garantizar que no queden procesos zombi en segundo plano.

### 2. Parche XML #2: Estricta Conformidad de Esquema Mathcad 5.0
- **Diagnóstico:** Modificaciones dinámicas en atributos no admitidos (como `display-width` colocado en etiquetas `<region>`) ocasionaban rechazo silencioso de la hoja.
- **Solución implementada:** Se aisló la edición de escala gráfica exclusivamente al nodo hijo `<picture><png display-width="..." display-height="..."/></picture>`, manteniendo la etiqueta `<region>` con sus atributos estrictos (`region-id`, `top`, `left`, `width`, `height`).

### 3. Parche AST #3: Encadenamiento Binario Asociativo Izquierdo en Macaulay
- **Diagnóstico:** Fórmulas algebraicas de singularidad con múltiples términos requerían una estructura de árbol binario estricta (`<apply><plus/><apply><minus/>...</apply></apply>`).
- **Solución implementada:** Creación del algoritmo `build_additive_chain()` en `mcdx_generator.py`, que ensambla recursivamente de izquierda a derecha todos los términos de apoyos, cargas uniformes de tramo activo, tramos superados, momentos y cargas puntuales.

### 4. Parche UI #4: Presets Rápidos y Redimensionamiento Adaptativo
- **Diagnóstico:** La entrada manual de hasta 10 tramos en un examen demanda rapidez para el alumno.
- **Solución implementada:** Se incorporó una barra superior con botones de acceso directo a los 6 casos de estudio más representativos. Se añadió redimensionamiento responsivo al lienzo canvas con el evento `<Configure>` y enlace directo al manual teórico en Markdown.

---

## 📐 Fundamento Teórico del Método

### 1. Funciones de Singularidad con Operadores Booleanos en Mathcad
En Mathcad Prime, las expresiones de comparación como `(x ≥ a)` o `(a > x > 0)` operan como **funciones escalón (Heaviside)**:
$$(x \ge a) = \begin{cases} 1 & \text{si } x \ge a \quad (\text{Verdadero}) \\ 0 & \text{si } x < a \quad (\text{Falso}) \end{cases}$$

Esto permite formular una sola función continua a trozos válida para toda la viga $[0, L_{\text{tot}}]$:

$$\begin{aligned}
M(x) := & + V_A \cdot x \\
& - (a > x > 0) \cdot q \cdot \frac{x^2}{2} \\
& - (x \ge a) \cdot q \cdot a \cdot \left(x - \frac{a}{2}\right) \\
& + (x \ge a) \cdot M \\
& - (x \ge a + b) \cdot P_1 \cdot (x - (a + b)) \\
& + (x \ge a + b + c) \cdot V_D \cdot (x - (a + b + c))
\end{aligned}$$

### 2. ¿Por qué se quitan los brazos en la función de cortante $Q(x)$?
Por la relación diferencial de equilibrio:
$$Q(x) = \frac{d M(x)}{dx}$$

Al derivar respecto a $x$:
- $\frac{d}{dx}(V_A \cdot x) = V_A \implies$ El brazo lineal desaparece.
- $\frac{d}{dx}\left(q \frac{x^2}{2}\right) = q \cdot x \implies$ La parábola se deriva a variación lineal.
- $\frac{d}{dx}\left[q \cdot a \left(x - \frac{a}{2}\right)\right] = q \cdot a \implies$ Queda la fuerza constante del tramo.
- $\frac{d}{dx}[M] = 0 \implies$ **¡Un momento concentrado no produce cortante!** Desaparece por completo en $Q(x)$.
- $\frac{d}{dx}[P_1 \cdot (x - x_1)] = P_1 \implies$ Queda la fuerza puntual pura.

### 3. Rango de Discretización Milimétrico
$$x := 0\text{ m}, 0.001\text{ m} .. L_{\text{tot}}$$
- Paso $\Delta x = 1\text{ mm}$: Genera miles de puntos de evaluación para trazar los saltos verticales instantáneos sin diagonales falsas.
- Localiza con precisión milimétrica la coordenada de cortante cero donde ocurre el momento máximo ($M_{\max}$).

---

## 🚀 Instalación y Uso

### Requisitos
- Windows 10 u 11 (64-bit).
- Python 3.10 o superior.
- PTC Mathcad Prime 11.0.0.

### Dependencias de Python
```bash
pip install pillow pywin32
```

### Ejecución de la Aplicación Gráfica
Haga doble clic en el archivo:
```text
INICIAR_APP_VIGAS.bat
```
o ejecute desde la terminal:
```bash
python app_gui.py
```

### Ejecución de las 10 Pruebas Automatizadas
```bash
python run_10_tests.py
```

---

## 📂 Estructura del Repositorio

```text
diagramas-en-MATHCAD/
├── app_gui.py                            # Interfaz gráfica de escritorio con presets y preview en vivo
├── beam_engine.py                        # Motor analítico y generador de gráficos vectoriales con cortes
├── mcdx_generator.py                     # Constructor dinámico de paquetes OPC nativos .mcdx
├── run_10_tests.py                       # Batería de 10 pruebas de estrés automatizadas vía COM
├── build_template.py                     # Generador de la plantilla base validada de 10 tramos
├── mcdx_toolkit.py                       # Utilidades de inspección y validación OPC
├── INICIAR_APP_VIGAS.bat                 # Acceso directo para iniciar la interfaz gráfica
├── ABRIR_PLANTILLA_MATHCAD.bat           # Acceso directo para abrir la plantilla en Mathcad Prime
├── FORMULARIO_Y_MANUAL_MATHCAD_VIGAS.md  # Manual teórico y formulario exhaustivo paso a paso
├── EJERCICIO-01.mcdx                     # Plantilla base oficial del examen
├── PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx# Archivo de cálculo de 10 tramos verificado
├── PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.pdf # Memoria de cálculo en PDF vectorial (460 KB)
├── test_outputs/                         # Salidas verificadas de las 10 pruebas (.mcdx y .pdf)
├── README.md                             # Documentación oficial del proyecto
└── LICENSE                               # Licencia MIT
```

---

## 👤 Autor
Desarrollado para **Análisis Estructural II** por **[72008081-pixel](https://github.com/72008081-pixel)**.
