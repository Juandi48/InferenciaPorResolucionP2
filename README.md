# 🧠 Proyecto 2 — Motor de Inferencia por Resolución (Lógica de Primer Orden)

Autor: **Juan Diego Rojas Vargas**  
Materia: **Inteligencia Artificial**  
Versión: **Final – Interfaz Mejorada con Guía FOL y Reporte Automático**

---

## 📘 Descripción

Este programa implementa un **motor de inferencia basado en resolución**, capaz de:
- Aceptar **fórmulas en Lógica de Primer Orden (FOL)**.
- Convertirlas automáticamente a **Forma Normal Conjuntiva (FNC)**.
- Aplicar el **algoritmo de resolución con unificación (MGU)**.
- Mostrar todo el proceso paso a paso y guardar un reporte completo en `reporte_resolucion.txt`.

Se incluye además una **guía interactiva de escritura FOL** para facilitar el uso desde la consola.

---

## 🧩 Dependencias

Este proyecto **solo requiere Python estándar (sin bibliotecas externas)**.

Funciona con **Python 3.8 o superior**.

Sin embargo, se recomienda crear un entorno virtual para mantener el entorno limpio.

### 🔧 Instalación de Python

Si no tienes Python, descárgalo desde [python.org/downloads](https://www.python.org/downloads/)  
y asegúrate de marcar la opción **"Add Python to PATH"** durante la instalación.

---

## 🧱 Estructura del Proyecto



InferenciaPorResolucionP2/
│
├── Proyecto2.py # Código principal
├── reporte_resolucion.txt # (Se genera automáticamente al ejecutar)
└── README.md # Este archivo


---

## ⚙️ Ejecución

Abre una terminal o consola en la carpeta del proyecto y ejecuta:

```bash
python Proyecto2.py


Si tienes varios Python instalados, usa:

python3 Proyecto2.py

💡 Cómo usar el programa

Al iniciar, el programa mostrará la guía rápida de escritura FOL:

=== Motor de Inferencia por Resolución (Entrada en FOL) ===
Guía rápida de escritura FOL:

┌──────────────────────────┬───────────────────────┬────────────────────────────┬──────────────────────────────────────────────┐
│ Conectivo / cuantificador │ Cómo escribirlo       │ También acepta             │ Ejemplos válidos                             │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ Para todo                │ forall                │ ∀                         │ forall x: P(x) -> Q(x)                       │
│ Existe (consecuente)     │ exists                │ ∃                         │ forall x: P(x) -> (exists z: R(z,x))         │
│ Y / Conjunción           │ ^                     │ &  o  ∧                   │ forall x: (A(x) ^ B(x)) -> C(x)              │
│ O / Disyunción           │ v                     │ ∨                         │ P(a) v Q(b)                                  │
│ Implicación              │ ->                    │ →                         │ forall x: P(x) -> Q(x)                       │
│ Negación                 │ ¬                     │ (recomendado usar ¬)       │ forall x: (A(x) ^ B(x)) -> ¬C(x)             │
└──────────────────────────┴───────────────────────┴────────────────────────────┴──────────────────────────────────────────────┘
Use 'fin' para terminar la base de conocimiento.


Luego, deberás ingresar las fórmulas de tu Base de Conocimiento (BK) una por una, por ejemplo:

1. Hombre(Marco)
2. Pompeyano(Marco)
3. forall x: Pompeyano(x) -> Romano(x)
4. Gobernante(Cesar)
5. forall x: Romano(x) -> (Leal(x,Cesar) v Odia(x,Cesar))
6. forall x,y: (Hombre(x) ^ Gobernante(y) ^ IntentaAsesinar(x,y)) -> ¬Leal(x,y)
7. IntentaAsesinar(Marco,Cesar)
8. fin


Después, el programa te pedirá la pregunta a demostrar, por ejemplo:

Pregunta (en FOL, ej: Odia(Marco,Cesar)): Odia(Marco,Cesar)

🧾 Resultado

El programa mostrará:

Las cláusulas resultantes (FNC).

El proceso completo de resolución paso a paso.

Una conclusión final, por ejemplo:

✓ Se derivó la cláusula vacía → Conclusión demostrada

Conclusión: Sí, Odia(Marco,Cesar) ✅


Además, se genera automáticamente un archivo reporte_resolucion.txt con todos los pasos del proceso.

🧠 Ejemplo de uso rápido
Base de conocimiento:
1. forall x: Gato(x) -> Animal(x)
2. Gato(Tuna)
3. forall x: (Animal(x) ^ Ama(Jack,x)) -> (exists z: Ama(z,Jack))
4. forall x,y: (Animal(y) ^ Mata(x,y)) -> (forall z: ¬Ama(z,x))
5. forall y: Animal(y) -> Ama(Jack,y)
6. Mata(Jack,Tuna) v Mata(Curiosidad,Tuna)
7. fin

Pregunta:
Mata(Curiosidad,Tuna)

Resultado:
✓ Se derivó la cláusula vacía → Conclusión demostrada
Conclusión: Sí, Mata(Curiosidad,Tuna) ✅

📄 Reporte de resolución

Se genera automáticamente un archivo de texto:

reporte_resolucion.txt


Este archivo incluye:

Fecha y hora de ejecución

Todas las cláusulas resolventes

Resultado final de la inferencia

🧰 Comandos útiles (Windows / Linux / macOS)
Ver versión de Python:
python --version

Crear entorno virtual (opcional):
python -m venv venv

Activarlo:

Windows:

venv\Scripts\activate


Linux / macOS:

source venv/bin/activate

Ejecutar el programa:
python Proyecto2.py

🧩 Tecnologías y características clave

Python 3 (sin librerías externas)

Expresiones regulares (re)

Combinaciones de cláusulas (itertools)

Registro automático con timestamp (datetime)

Colores ANSI para consola (compatible con Windows, macOS, Linux)

Implementación de unificación simbólica (MGU)

Conversión automática FOL → FNC

Sistema de resolución binaria con trazado paso a paso

🏁 Créditos

Desarrollado por Juan Diego Rojas Vargas, Juan Martin Trejos, Victoria Elizabeth Roa González y Hania Valentina Carreño Baquero
Universidad / Asignatura: Inteligencia Artificial – Proyecto 2
Lenguaje: Python 3

© 2025 Juan Diego Rojas Vargas. Todos los derechos reservados.
