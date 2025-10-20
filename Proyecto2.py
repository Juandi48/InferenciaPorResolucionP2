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
    """
    Conversor FOL -> FNC para los patrones del curso, con skolemización básica:
      - Hechos:                 P(a), P(a) ∨ Q(b)
      - ∀…: A(x) -> B(x)
      - ∀…: A(x) -> (B(x) ∨ C(x))
      - ∀…: (A ^ B ^ ...) -> ¬D
      - ∀…: (A ^ B ^ ...) -> ∃v  T(...)
      - ∀…: (A ^ B ^ ...) -> ∀v  ¬T(...)

    Notas:
      - Usa '∧' o '&' para AND y '∨' o 'v' para OR.
      - Para '∃v' en el consecuente, crea función de Skolem f_v(universales_en_alcance).
      - Si no hay universales, usa constante Skolem c_v.
    """
    def norm(s):
        return (s.replace(" ", "")
                 .replace("∀", "forall")
                 .replace("∧", "^").replace("&", "^")
                 .replace("∨", "v").replace("→", "->"))

    def split_conj(s):
        return [p for p in s.split("^") if p]

    def split_disj(s):
        return [p for p in s.split("v") if p]

    def negate(atom):
        return atom if atom.startswith("¬") else f"¬{atom}"

    def skolemize_existential(pred_str, evars, uvars):
        """
        Reemplaza cada existencial 'v' en pred_str por f_v(uvars) o c_v si uvars=[]
        pred_str: e.g. 'Ama(z,x)'
        evars:    lista de variables existenciales, e.g. ['z']
        uvars:    lista de variables universales en alcance, e.g. ['x','y']
        """
        out = pred_str
        args = ",".join(uvars)
        for v in evars:
            if uvars:
                sk = f"f_{v}({args})"
            else:
                sk = f"c_{v}"
            out = re.sub(rf"\b{v}\b", sk, out)
        return out

    clauses = []

    for f in fols:
        s = norm(f)

        # 0) Hecho disyuntivo directo:  P(...) v Q(...)  (lo tomamos como cláusula)
        if ("forall" not in s) and ("->" not in s) and ("v" in s):
            parts = split_disj(s)
            clauses.append(set(parts))
            continue

        # 1) Hecho unario:  P(...)
        if ("forall" not in s) and ("->" not in s):
            clauses.append({s})
            continue

        # 2) forall U: Ante -> Cons
        m = re.match(r"^forall([a-z,]+):(.+)->(.+)$", s)
        if not m:
            # formato no soportado
            continue

        uvars = [v for v in m.group(1).split(",") if v]      # universales
        antecedent = m.group(2)
        consequent = m.group(3)

        # 2.a) Antecedente puede venir parentetizado; normalizamos
        if antecedent.startswith("(") and antecedent.endswith(")"):
            antecedent = antecedent[1:-1]
        ants = split_conj(antecedent) if "^" in antecedent else [antecedent]

        # helper: negaciones del antecedente
        neg_ants = {negate(a) if not a.startswith("¬") else a for a in ants}

        # CASOS DEL CONSECUENTE:

        # (i) exists v: T(...)
        m_ex = re.match(r"^\(exists([a-z,]+):([A-Za-z]+\([A-Za-z0-9_,]+\))\)$", consequent)
        if m_ex:
            evars = [v for v in m_ex.group(1).split(",") if v]
            T = m_ex.group(2)
            T_skol = skolemize_existential(T, evars, uvars)
            clauses.append(neg_ants | {T_skol})
            continue

        # (ii) forall w: ¬T(...)
        m_all_not = re.match(r"^\(forall([a-z,]+):¬([A-Za-z]+\([A-Za-z0-9_,]+\))\)$", consequent)
        if m_all_not:
            # Las variables 'w' simplemente quedan como variables libres (universales) en la cláusula
            T = m_all_not.group(2)
            clauses.append(neg_ants | {negate(T)})
            continue

        # (iii) Disyunción explícita en el consecuente:  (B v C v ...)
        if consequent.startswith("(") and consequent.endswith(")") and "v" in consequent:
            parts = set(split_disj(consequent[1:-1]))
            clauses.append(neg_ants | parts)
            continue

        # (iv) Simple: P(...)  (=> ¬A v P)
        clauses.append(neg_ants | {consequent})

    # Negación de la pregunta
    q = norm(pregunta)
    clauses.append({negate(q)})

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
