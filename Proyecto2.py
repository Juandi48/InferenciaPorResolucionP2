# -*- coding: utf-8 -*-
"""
Proyecto 2 — Motor de Inferencia basado en Resolución (Bonito y con Reporte)
Autor: Juan Diego Rojas Vargas

Incluye:
 - Entrada en Lógica de Primer Orden (FOL)
 - Resolución con Unificación (MGU)
 - Salida formateada con colores y estructura
 - Reporte completo en archivo 'reporte_resolucion.txt'
"""

import re
from itertools import combinations
from datetime import datetime

# Colores ANSI
class c:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

# ---------------------------
# Limpieza y utilidades
# ---------------------------
def limpiar(s):
    return (s.replace(" ", "")
             .replace("∀", "forall")
             .replace("^", "∧")
             .replace("v", "∨")
             .replace("→", "->")
             .strip())

# ---------------------------
# Conversión FOL → FNC
# ---------------------------
def fol_a_fnc_clausulas(fols, pregunta):
    clauses = []

    for f in fols:
        f = limpiar(f)

        # Hechos directos
        if "forall" not in f and "->" not in f:
            clauses.append({f})
            continue

        # Reglas tipo: forall x: P(x) -> Q(x)
        m = re.match(r"^forall[ a-z,]*:([A-Za-z]+\([a-zA-Z,]+\))->([A-Za-z]+\([a-zA-Z,]+\))$", f)
        if m:
            clauses.append({f"¬{m.group(1)}", m.group(2)})
            continue

        # Reglas tipo: forall x: P(x) -> (Q(x) ∨ R(x))
        m = re.match(r"^forall[ a-z,]*:([A-Za-z]+\([a-zA-Z,]+\))->\((.+)\)$", f)
        if m:
            ant = m.group(1)
            cons = [p.strip() for p in m.group(2).split("∨")]
            clauses.append({f"¬{ant}", *cons})
            continue

        # Reglas tipo: forall x,y: (A ∧ B ∧ C) -> ¬D
        m = re.match(r"^forall[ a-z,]*:\((.+)\)->(¬[A-Za-z]+\([a-zA-Z,]+\))$", f)
        if m:
            ants = [p.strip() for p in m.group(1).split("∧")]
            cons = m.group(2)
            neg_ants = {f"¬{a}" if not a.startswith("¬") else a for a in ants}
            clauses.append(neg_ants | {cons})
            continue

    # Agregar negación de la pregunta
    q = limpiar(pregunta)
    if not q.startswith("¬"):
        clauses.append({f"¬{q}"})
    else:
        clauses.append({q})
    return clauses

# ---------------------------
# Unificación (MGU)
# ---------------------------
def es_variable(x):
    return re.match(r'^[a-z]\w*$', x)

def parsear_atom(a):
    pred = a.split('(')[0]
    args = a[a.find('(')+1:a.find(')')].split(',')
    args = [arg.strip() for arg in args if arg.strip()]
    return pred, args

def unificar(x, y, theta=None):
    if theta is None:
        theta = {}
    if x == y:
        return theta
    if es_variable(x):
        theta[x] = y
        return theta
    if es_variable(y):
        theta[y] = x
        return theta
    p1, a1 = parsear_atom(x)
    p2, a2 = parsear_atom(y)
    if p1 != p2 or len(a1) != len(a2):
        return None
    for s1, s2 in zip(a1, a2):
        theta = unificar(s1, s2, theta)
        if theta is None:
            return None
    return theta

def aplicar_sust(clause, theta):
    nueva = set()
    for lit in clause:
        for var, val in theta.items():
            lit = re.sub(rf'\b{var}\b', val, lit)
        nueva.add(lit)
    return nueva

# ---------------------------
# Resolución con unificación integrada
# ---------------------------
def complementarios_con_unificacion(lit1, lit2):
    neg1, neg2 = lit1.startswith("¬"), lit2.startswith("¬")
    if neg1 == neg2:
        return None
    base1, base2 = (lit1[1:] if neg1 else lit1), (lit2[1:] if neg2 else lit2)
    return unificar(base1, base2, {})

def resolver(ci, cj):
    resolvents = set()
    for di in ci:
        for dj in cj:
            theta = complementarios_con_unificacion(di, dj)
            if theta is not None:
                nueva = aplicar_sust(ci - {di}, theta) | aplicar_sust(cj - {dj}, theta)
                resolvents.add(frozenset(nueva))
    return resolvents

# ---------------------------
# Motor de resolución con formato bonito
# ---------------------------
def resolucion(clauses, verbose=True, guardar=True):
    new = set()
    paso = 1
    reporte = []
    print(f"\n{c.HEADER}=== Proceso de Resolución ==={c.ENDC}")

    while True:
        pares = list(combinations(clauses, 2))
        for (ci, cj) in pares:
            resolvents = resolver(ci, cj)
            for r in resolvents:
                linea = f"Paso {paso:03}: {set(ci)} ⊗ {set(cj)} ⟹ {set(r)}"
                reporte.append(linea)
                if verbose:
                    print(f"{c.OKBLUE}Paso {paso:03}:{c.ENDC} {set(ci)} {c.BOLD}⊗{c.ENDC} {set(cj)} {c.OKCYAN}⟹{c.ENDC} {set(r)}")
                paso += 1
                if frozenset() in resolvents:
                    print(f"\n{c.OKGREEN}✓ Se derivó la cláusula vacía → Conclusión demostrada{c.ENDC}")
                    if guardar:
                        guardar_reporte(reporte, True)
                    return True
            new = new.union(resolvents)
        if new.issubset(set(map(frozenset, clauses))):
            print(f"\n{c.FAIL}✗ No se pudo derivar la cláusula vacía → Conclusión no demostrada{c.ENDC}")
            if guardar:
                guardar_reporte(reporte, False)
            return False
        for c_ in new:
            if c_ not in clauses:
                clauses.append(c_)

# ---------------------------
# Guardar reporte
# ---------------------------
def guardar_reporte(pasos, exito):
    nombre = "reporte_resolucion.txt"
    with open(nombre, "w", encoding="utf-8") as f:
        f.write("Reporte de Inferencia por Resolución\n")
        f.write(f"Generado: {datetime.now()}\n\n")
        for p in pasos:
            f.write(p + "\n")
        f.write("\nResultado final:\n")
        if exito:
            f.write("✓ Se derivó la cláusula vacía → Conclusión demostrada\n")
        else:
            f.write("✗ No se pudo derivar la cláusula vacía → Conclusión no demostrada\n")
    print(f"\n{c.OKGREEN}📄 Reporte guardado como 'reporte_resolucion.txt'{c.ENDC}")

# ---------------------------
# Interfaz
# ---------------------------
def main():
    print(f"{c.HEADER}=== Motor de Inferencia por Resolución (Entrada en FOL) ==={c.ENDC}")
    print("Ingrese las fórmulas de la base de conocimiento en FOL.")
    print("Use 'forall' para cuantificadores y '¬' para negaciones.")
    print("Ejemplo:")
    print("  Hombre(Marco)")
    print("  Pompeyano(Marco)")
    print("  forall x: Pompeyano(x) -> Romano(x)")
    print("  fin\n")

    base = []
    while True:
        s = input(f"  {len(base)+1}. ").strip()
        if s.lower() == "fin":
            break
        if s:
            base.append(s)

    pregunta = input(f"\n{c.OKCYAN}Pregunta (en FOL, ej: Odia(Marco,Cesar)): {c.ENDC}").strip()

    clauses = fol_a_fnc_clausulas(base, pregunta)
    print(f"\n{c.BOLD}=== Cláusulas (FNC) ==={c.ENDC}")
    for i, c_ in enumerate(clauses, 1):
        print(f"{i}. {c_}")

    resultado = resolucion([frozenset(c_) for c_ in clauses], verbose=True)
    if resultado:
        print(f"\n{c.OKGREEN}Conclusión: Sí, {pregunta} ✅{c.ENDC}")
    else:
        print(f"\n{c.FAIL}Conclusión: No se puede demostrar que {pregunta} ❌{c.ENDC}")

if __name__ == "__main__":
    main()
