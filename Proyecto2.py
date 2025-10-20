# -*- coding: utf-8 -*-
"""
Motor de Inferencia por Resolución con conversión desde Lenguaje Natural
Pontificia Universidad Javeriana – Proyecto 2
Autores: Juan Diego Rojas Vargas, Juan Martin Trejos, Victoria Elizabeth Roa González y Hania Valentina Carreño Baquero
"""

import spacy
from sympy.logic.boolalg import to_cnf, Or, And, Not, Symbol
from itertools import combinations

# Cargar modelo de lenguaje
nlp = spacy.load("es_core_news_sm")

# -----------------------------------------
# 1. Conversión Lenguaje Natural → Lógica
# -----------------------------------------

def oracion_a_predicado(oracion):
    """
    Convierte una oración simple a una representación lógica simbólica.
    (Versión simplificada para demostración)
    """
    doc = nlp(oracion)
    sujeto, verbo, objeto = None, None, None

    for token in doc:
        if token.dep_ == "nsubj":
            sujeto = token.text.capitalize()
        elif token.pos_ == "VERB":
            verbo = token.lemma_.capitalize()
        elif token.dep_ in ("obj", "obl"):
            objeto = token.text.capitalize()

    if sujeto and verbo and objeto:
        return f"{verbo}({sujeto},{objeto})"
    elif sujeto and verbo:
        return f"{verbo}({sujeto})"
    else:
        return oracion

# -----------------------------------------
# 2. Conversión a FNC
# -----------------------------------------

def convertir_a_FNC(predicado):
    """
    Convierte una fórmula simbólica (string) a Forma Normal Conjuntiva (FNC)
    usando sympy.
    """
    expr = predicado.replace("¬", "~").replace("∨", "|").replace("∧", "&").replace("⇒", ">>")
    try:
        return to_cnf(expr, simplify=True)
    except Exception:
        return predicado

# -----------------------------------------
# 3. Resolución por refutación
# -----------------------------------------

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
            print("✗ No se pudo derivar la cláusula vacía")
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)

# -----------------------------------------
# 4. Ejemplo práctico
# -----------------------------------------

base_conocimiento = [
    "Marco es un hombre.",
    "Marco es un Pompeyano.",
    "Todos los Pompeyanos son Romanos.",
    "César es un gobernante.",
    "Todos los Romanos son o leales al César o odian al César.",
    "La gente solo intenta asesinar a los gobernantes a los que no es leal.",
    "Marco intentó asesinar al César."
]

pregunta = "¿Marco odia al César?"

print("=== BASE DE CONOCIMIENTO ===")
for oracion in base_conocimiento:
    print(f"- {oracion}")

# Conversión a predicados
predicados = [oracion_a_predicado(o) for o in base_conocimiento]
print("\n=== PREDICADOS GENERADOS ===")
for p in predicados:
    print(p)

# Para simplificación: simulamos FNC según el ejemplo clásico
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

print("\n=== RESOLUCIÓN ===")
resolution_algorithm([frozenset(c) for c in clauses])
