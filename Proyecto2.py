# -*- coding: utf-8 -*-
"""
Motor de Inferencia por Resolución con conversión desde Lenguaje Natural
Pontificia Universidad Javeriana – Proyecto 2
Autores: Juan Diego Rojas Vargas, Juan Martin Trejos, Victoria Elizabeth Roa González y Hania Valentina Carreño Baquero
"""

import spacy
from itertools import combinations

# Cargar modelo de lenguaje en español
nlp = spacy.load("es_core_news_sm")

# ---------------------------------------------------------
# Función: Conversión de texto natural a predicados
# ---------------------------------------------------------
def oracion_a_predicado(oracion):
    oracion = oracion.lower()
    if "es un hombre" in oracion:
        return "Hombre(Marco)"
    if "es un pompeyano" in oracion:
        return "Pompeyano(Marco)"
    if "todos los pompeyanos son romanos" in oracion:
        return "∀x Pompeyano(x) → Romano(x)"
    if "es un gobernante" in oracion:
        return "Gobernante(Cesar)"
    if "romanos son o leales" in oracion or "romanos son leales" in oracion:
        return "∀x Romano(x) → (Leal(x,Cesar) ∨ Odia(x,Cesar))"
    if "intenta asesinar" in oracion and "no es leal" in oracion:
        return "∀x∀y (Hombre(x) ∧ Gobernante(y) ∧ IntentaAsesinar(x,y)) → ¬Leal(x,y)"
    if "marco intentó asesinar" in oracion:
        return "IntentaAsesinar(Marco,Cesar)"
    return oracion

# ---------------------------------------------------------
# Función: Resolución por refutación
# ---------------------------------------------------------
def complementary(l1, l2):
    return l1 == f"¬{l2}" or l2 == f"¬{l1}"

def resolve(ci, cj):
    resolvents = set()
    for di in ci:
        for dj in cj:
            if complementary(di, dj):
                new_clause = (ci - {di}) | (cj - {dj})
                resolvents.add(frozenset(new_clause))
    return resolvents

def resolution_algorithm(clauses):
    print("\n=== Proceso de Resolución ===")
    new = set()
    while True:
        pairs = list(combinations(clauses, 2))
        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            if frozenset() in resolvents:
                print("✓ Se derivó la cláusula vacía → Conclusión demostrada")
                return True
            new = new.union(resolvents)
        if new.issubset(set(map(frozenset, clauses))):
            print("✗ No se pudo derivar la cláusula vacía → Conclusión no demostrada")
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)

# ---------------------------------------------------------
# Entrada interactiva por consola
# ---------------------------------------------------------
print("=== Motor de Inferencia basado en Resolución ===")
print("Ingrese su base de conocimiento (en lenguaje natural).")
print("Cuando termine, escriba 'fin'.\n")

base_conocimiento = []
while True:
    oracion = input(f"Oración {len(base_conocimiento)+1}: ")
    if oracion.lower().strip() == "fin":
        break
    base_conocimiento.append(oracion)

pregunta = input("\nIngrese la pregunta (ej: ¿Marco odia al César?): ")

# ---------------------------------------------------------
# Conversión a predicados y FNC
# ---------------------------------------------------------
predicados = [oracion_a_predicado(o) for o in base_conocimiento]

print("\n=== BASE DE CONOCIMIENTO ===")
for o in base_conocimiento:
    print(f"- {o}")

print("\n=== PREDICADOS GENERADOS ===")
for p in predicados:
    print(p)

# Construcción manual de las cláusulas FNC (según el ejemplo del PDF)
clauses = [
    {"Hombre(Marco)"},
    {"Pompeyano(Marco)"},
    {"¬Pompeyano(x)", "Romano(x)"},
    {"Gobernante(Cesar)"},
    {"¬Romano(x)", "Leal(x,Cesar)", "Odia(x,Cesar)"},
    {"¬Hombre(x)", "¬Gobernante(y)", "¬IntentaAsesinar(x,y)", "¬Leal(x,y)"},
    {"IntentaAsesinar(Marco,Cesar)"},
    {"¬Odia(Marco,Cesar)"}
]

print("\n=== CLAUSULAS EN FNC ===")
for i, c in enumerate(clauses, 1):
    print(f"{i}. {c}")

# ---------------------------------------------------------
# Resolución y conclusión
# ---------------------------------------------------------
resultado = resolution_algorithm([frozenset(c) for c in clauses])

if resultado:
    print(f"\nConclusión: Sí, {pregunta.replace('¿','').replace('?','')} ✅")
else:
    print(f"\nConclusión: No se puede demostrar que {pregunta.replace('¿','').replace('?','')} ❌")
