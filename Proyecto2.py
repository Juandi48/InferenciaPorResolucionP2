# -*- coding: utf-8 -*-
"""
Motor de Inferencia basado en Resolución (con spaCy NLP generalizado)
Autor: Juan Diego Rojas Vargas

Funcionalidades:
 - Entrada en lenguaje natural
 - Extracción automática de sujeto–verbo–objeto con spaCy
 - Conversión a Lógica de Primer Orden (FOL)
 - Transformación a Forma Normal Conjuntiva (FNC)
 - Resolución por refutación con unificación (MGU)

Requisitos:
   pip install spacy
   python -m spacy download es_core_news_sm
"""

import re
import spacy
from itertools import combinations

# -----------------------------------------------------
# Cargar modelo de lenguaje
# -----------------------------------------------------
nlp = spacy.load("es_core_news_sm")

# -----------------------------------------------------
# Normalización de texto
# -----------------------------------------------------
def norm(s: str) -> str:
    s = s.strip().replace("¿", "").replace("?", "").replace(".", "")
    s = s.replace(",", "").lower()
    return s

# -----------------------------------------------------
# NLP → FOL (automático)
# -----------------------------------------------------
def sentence_to_fol(sentence: str):
    """
    Convierte una oración en español a un predicado lógico simple
    usando extracción de sujeto, verbo y objeto.
    """
    doc = nlp(sentence)
    sujeto, verbo, objeto = None, None, None

    for token in doc:
        # Sujeto (persona, entidad)
        if token.dep_ in ("nsubj", "nsubj:pass"):
            sujeto = token.text.capitalize()
        # Verbo principal
        if token.pos_ == "VERB":
            verbo = token.lemma_.capitalize()
        # Objeto directo o indirecto
        if token.dep_ in ("obj", "obl"):
            objeto = token.text.capitalize()

    if sujeto and verbo and objeto:
        return f"{verbo}({sujeto},{objeto})"
    elif sujeto and verbo:
        return f"{verbo}({sujeto})"
    else:
        # fallback: usa tokens principales
        tokens = [t.lemma_.capitalize() for t in doc if not t.is_stop]
        if len(tokens) == 1:
            return tokens[0]
        elif len(tokens) == 2:
            return f"{tokens[1]}({tokens[0]})"
        elif len(tokens) >= 3:
            return f"{tokens[1]}({tokens[0]},{tokens[2]})"
        else:
            return sentence

# -----------------------------------------------------
# Conversión a FNC (simplificada)
# -----------------------------------------------------
def fol_to_clauses(fols, question):
    clauses = []
    for f in fols:
        if "forall" in f or "→" in f or "->" in f:
            # ignoramos reglas universales complejas en este modo automático
            continue
        clauses.append({f})
    # negación de la pregunta
    q = question.replace(" ", "").replace("?", "")
    if not q.startswith("¬"):
        clauses.append({f"¬{q}"})
    return clauses

# -----------------------------------------------------
# Unificación
# -----------------------------------------------------
def is_var(x):
    return bool(re.match(r'^[a-z]\w*$', x))

def parse_atom(atom):
    pred = atom.split('(')[0]
    args = atom[atom.find('(')+1:atom.find(')')].split(',')
    args = [a.strip() for a in args]
    return pred, args

def unify(x, y, theta=None):
    if theta is None:
        theta = {}
    if x == y:
        return theta
    if is_var(x):
        theta[x] = y
        return theta
    if is_var(y):
        theta[y] = x
        return theta
    px, ax = parse_atom(x)
    py, ay = parse_atom(y)
    if px != py or len(ax) != len(ay):
        return None
    for a1, a2 in zip(ax, ay):
        theta = unify(a1, a2, theta)
        if theta is None:
            return None
    return theta

def apply_subst(clause, theta):
    new = set()
    for lit in clause:
        for var, val in theta.items():
            lit = re.sub(rf'\b{var}\b', val, lit)
        new.add(lit)
    return new

def complementary(a, b):
    return a == f"¬{b}" or b == f"¬{a}"

def resolve(ci, cj):
    resolvents = set()
    for di in ci:
        for dj in cj:
            if complementary(di, dj):
                di_clean = di.replace("¬", "")
                dj_clean = dj.replace("¬", "")
                theta = unify(di_clean, dj_clean, {})
                if theta is not None:
                    new_clause = (apply_subst(ci - {di}, theta) |
                                  apply_subst(cj - {dj}, theta))
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

# -----------------------------------------------------
# Interfaz por consola
# -----------------------------------------------------
def main():
    print("=== Motor de Inferencia con NLP (spaCy) ===")
    print("Ingrese su base de conocimiento en lenguaje natural.")
    print("Escriba 'fin' para terminar.\n")

    base = []
    while True:
        s = input(f"  {len(base)+1}. ").strip()
        if s.lower() == "fin":
            break
        if s:
            base.append(s)

    pregunta = input("\nPregunta: ").strip()

    # Paso 1: NL → FOL
    fols = [sentence_to_fol(s) for s in base]
    print("\n=== FOL generado ===")
    for f in fols:
        print(" -", f)

    # Paso 2: FOL → FNC (simplificada)
    clauses = fol_to_clauses(fols, sentence_to_fol(pregunta))
    print("\n=== Cláusulas FNC ===")
    for i, c in enumerate(clauses, 1):
        print(f" {i}. {c}")

    # Paso 3: Resolución
    result = resolution_algorithm([frozenset(c) for c in clauses])
    if result:
        print(f"\nConclusión: Sí, {pregunta} ✅")
    else:
        print(f"\nConclusión: No se puede demostrar que {pregunta} ❌")

if __name__ == "__main__":
    main()
