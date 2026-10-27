# Diagramas en Mathcad — Generador Automatizado para PTC Mathcad Prime 11

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Mathcad](https://img.shields.io/badge/PTC%20Mathcad-Prime%2011.0.0-orange?logo=mathcad&logoColor=white)](https://www.mathcad.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-72008081--pixel-purple?logo=github)](https://github.com/72008081-pixel)

Suite de escritorio interactiva y generador de memorias de cálculo para el análisis de vigas isostáticas e hiperestáticas en **PTC Mathcad Prime 11.0.0**. Implementa el método de **Funciones de Singularidad / Macaulay mediante operadores booleanos** para producir automáticamente las funciones seccionales, el cálculo de reacciones y los diagramas en vivo de **Fuerza Cortante (DFC)** y **Momento Flector (DMF)**.

---

## 🌟 Características Principales

1. **Interfaz Gráfica de Escritorio (Desktop GUI):**
   - Panel de control intuitivo con pestañas dedicadas para **Tramos ($L_1 \dots L_{10}$)**, **Apoyos (Fijo, Móvil, Empotramiento)**, **Cargas Distribuidas ($q$)**, **Cargas Puntuales ($P$)** y **Momentos Concentrados ($M$)**.
   - Selector dinámico de 1 a 10 tramos con cálculo automático de coordenadas nodales ($x_0, x_1, \dots, x_n$) y longitud total $L_{\text{tot}}$.
2. **Previsualizador Vectorial en Tiempo Real (Canvas 2D):**
   - Dibuja la viga a escala proporcional mientras el usuario escribe los datos.
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
   - Exportación directa a PDF vectorial de alta resolución sin necesidad de manipular Mathcad manualmente.

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
Por la relación diferencial de Navier-Euler:
$$Q(x) = \frac{d M(x)}{dx}$$

Al derivar respecto a $x$:
- $\frac{d}{dx}(V_A \cdot x) = V_A \implies$ El brazo lineal desaparece.
- $\frac{d}{dx}\left(q \frac{x^2}{2}\right) = q \cdot x \implies$ La parábola se deriva a variación lineal.
- $\frac{d}{dx}\left[q \cdot a \left(x - \frac{a}{2}\right)\right] = q \cdot a \implies$ Queda la fuerza constante del tramo.
- $\frac{d}{dx}[M] = 0 \implies$ **¡Un momento concentrado no produce cortante!** Desaparece por completo en $Q(x)$.
- $\frac{d}{dx}[P_1 \cdot (x - x_1)] = P_1 \implies$ Queda la fuerza puntual pura.

### 3. Rango de Discretización Milimétrico
$$x := 0\text{ m}, 0.001\text{ m} .. L_{\text{tot}}$$
- Paso $\Delta x = 1\text{ mm}$: Genera $5001$ puntos de evaluación para una viga de $5\text{ m}$.
- Permite trazar los saltos verticales instantáneos de cortante y momento sin líneas diagonales falsas.
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

### Ejecución Rápida
Haga doble clic en el archivo:
```text
INICIAR_APP_VIGAS.bat
```
o ejecute desde la terminal:
```bash
python app_gui.py
```

---

## 📂 Estructura del Repositorio

```text
diagramas-en-MATHCAD/
├── app_gui.py                            # Interfaz gráfica interactiva de escritorio (Tkinter)
├── beam_engine.py                        # Motor analítico y renderizador de esquema con cortes
├── mcdx_generator.py                     # Generador del paquete OPC ZIP nativo de Mathcad Prime
├── build_template.py                     # Ensamblador de plantilla matemática en XML/MathML
├── mcdx_toolkit.py                       # CLI de automatización COM con Mathcad Prime 11
├── INICIAR_APP_VIGAS.bat                 # Lanzador de la aplicación de escritorio
├── ABRIR_PLANTILLA_MATHCAD.bat           # Acceso directo para abrir la plantilla en Mathcad Prime
├── FORMULARIO_Y_MANUAL_MATHCAD_VIGAS.md  # Manual teórico y formulario exhaustivo paso a paso
├── EJERCICIO-01.mcdx                     # Plantilla base oficial del examen
├── PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.mcdx# Archivo de cálculo nativo pre-calculado
├── PLANTILLA_MAESTRA_10_TRAMOS_VIGAS.pdf # Memoria de cálculo en PDF vectorial
├── README.md                             # Documentación oficial del proyecto
└── LICENSE                               # Licencia MIT
```

---

## 👤 Autor
Desarrollado para **Análisis Estructural II** por **[72008081-pixel](https://github.com/72008081-pixel)**.
