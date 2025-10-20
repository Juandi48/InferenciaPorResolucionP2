# -*- coding: utf-8 -*-
"""
Proyecto 2 — Motor de Inferencia basado en Resolución (Bonito y con Reporte)
Autor: Juan Diego Rojas Vargas

Incluye:
 - Entrada en Lógica de Primer Orden (FOL)
 - Conversión FOL → FNC (Forma Normal Conjuntiva) con skolemización básica
 - Resolución con Unificación (MGU)
 - Salida formateada con colores y estructura
 - Reporte completo en archivo 'reporte_resolucion.txt'

───────────────────────────────────────────────────────────────
1) Cómo escribir FOL en tu programa (chuleta rápida)

El parser acepta fórmulas en texto plano, con las siguientes
convenciones. Internamente el sistema las convierte a FNC.

┌──────────────────────────┬───────────────────────┬────────────────────────────┬──────────────────────────────────────────────┐
│ Conectivo / cuantificador │ Cómo escribirlo       │ También acepta             │ Ejemplos válidos                             │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ Para todo                │ forall                │ ∀                         │ forall x: P(x) -> Q(x)                       │
│                          │                       │                           │ forall x,y: (A(x) ^ B(y)) -> C(x,y)          │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ Existe (en el consecuente)│ exists                │ ∃ (si se añade reemplazo) │ forall x: P(x) -> (exists z: R(z,x))         │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ Y / Conjunción           │ ^                     │ &  o  ∧                   │ forall x: (A(x) ^ B(x)) -> C(x)              │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ O / Disyunción           │ v                     │ ∨                         │ P(a) v Q(b)                                  │
│                          │                       │                           │ forall x: A(x) -> (B(x) v C(x))              │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ Implicación              │ ->                    │ →                         │ forall x: P(x) -> Q(x)                       │
├──────────────────────────┼───────────────────────┼────────────────────────────┼──────────────────────────────────────────────┤
│ Negación                 │ ¬                     │ (recomendado usar ¬ tal    │ forall x: (A(x) ^ B(x)) -> ¬C(x)             │
│                          │                       │ cual)                     │                                              │
└──────────────────────────┴───────────────────────┴────────────────────────────┴──────────────────────────────────────────────┘

Notas:
- Las reglas soportan "forall" en el antecedente y "exists" o "forall"
  dentro del consecuente.
- Los existenciales sólo deben aparecer en el consecuente.
- Puedes escribir '∧', '∨', '→' y '∀'; el programa los normaliza.
- Usa 'fin' para indicar el final de la base de conocimiento.
───────────────────────────────────────────────────────────────
"""

import re
from itertools import combinations
from datetime import datetime

# ---------------------------
# Colores ANSI
# ---------------------------
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
# Conversión FOL → FNC
# ---------------------------
def fol_a_fnc_clausulas(fols, pregunta):
    def norm(s):
        return (s.replace(" ", "")
                 .replace("∀", "forall")
                 .replace("∃", "exists")
                 .replace("∧", "^").replace("&", "^")
                 .replace("∨", "v").replace("→", "->"))

    def split_conj(s): return [p for p in s.split("^") if p]
    def split_disj(s): return [p for p in s.split("v") if p]
    def negate(atom): return atom if atom.startswith("¬") else f"¬{atom}"

    def skolemize_existential(pred_str, evars, uvars):
        out = pred_str
        args = ",".join(uvars)
        for v in evars:
            sk = f"f_{v}({args})" if uvars else f"c_{v}"
            out = re.sub(rf"\b{v}\b", sk, out)
        return out

    clauses = []

    for f in fols:
        s = norm(f)

        # Hecho disyuntivo
        if ("forall" not in s) and ("->" not in s) and ("v" in s):
            parts = split_disj(s)
            clauses.append(set(parts))
            continue

        # Hecho simple
        if ("forall" not in s) and ("->" not in s):
            clauses.append({s})
            continue

        # Regla general forall x,y: A -> B
        m = re.match(r"^forall([a-z,]+):(.+)->(.+)$", s)
        if not m:
            continue
        uvars = [v for v in m.group(1).split(",") if v]
        antecedent = m.group(2)
        consequent = m.group(3)

        if antecedent.startswith("(") and antecedent.endswith(")"):
            antecedent = antecedent[1:-1]
        ants = split_conj(antecedent) if "^" in antecedent else [antecedent]
        neg_ants = {negate(a) if not a.startswith("¬") else a for a in ants}

        # exists en el consecuente
        m_ex = re.match(r"^\(exists([a-z,]+):([A-Za-z]+\([A-Za-z0-9_,]+\))\)$", consequent)
        if m_ex:
            evars = [v for v in m_ex.group(1).split(",") if v]
            T = m_ex.group(2)
            T_skol = skolemize_existential(T, evars, uvars)
            clauses.append(neg_ants | {T_skol})
            continue

        # forall negado
        m_all_not = re.match(r"^\(forall([a-z,]+):¬([A-Za-z]+\([A-Za-z0-9_,]+\))\)$", consequent)
        if m_all_not:
            T = m_all_not.group(2)
            clauses.append(neg_ants | {negate(T)})
            continue

        # Disyunción en consecuente
        if consequent.startswith("(") and consequent.endswith(")") and "v" in consequent:
            parts = set(split_disj(consequent[1:-1]))
            clauses.append(neg_ants | parts)
            continue

        # Simple
        clauses.append(neg_ants | {consequent})

    # Negación de la consulta
    q = norm(pregunta)
    clauses.append({negate(q)})
    return clauses

# ---------------------------
# Unificación
# ---------------------------
def es_variable(x): return re.match(r'^[a-z]\w*$', x)

def parsear_atom(a):
    pred = a.split('(')[0]
    args = a[a.find('(')+1:a.find(')')].split(',')
    args = [arg.strip() for arg in args if arg.strip()]
    return pred, args

def unificar(x, y, theta=None):
    if theta is None: theta = {}
    if x == y: return theta
    if es_variable(x): theta[x] = y; return theta
    if es_variable(y): theta[y] = x; return theta
    p1, a1 = parsear_atom(x); p2, a2 = parsear_atom(y)
    if p1 != p2 or len(a1) != len(a2): return None
    for s1, s2 in zip(a1, a2):
        theta = unificar(s1, s2, theta)
        if theta is None: return None
    return theta

def aplicar_sust(clause, theta):
    nueva = set()
    for lit in clause:
        for var, val in theta.items():
            lit = re.sub(rf'\b{var}\b', val, lit)
        nueva.add(lit)
    return nueva

# ---------------------------
# Resolución con unificación
# ---------------------------
def complementarios_con_unificacion(lit1, lit2):
    neg1, neg2 = lit1.startswith("¬"), lit2.startswith("¬")
    if neg1 == neg2: return None
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
    new = set(); paso = 1; reporte = []
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
                    if guardar: guardar_reporte(reporte, True)
                    return True
            new = new.union(resolvents)
        if new.issubset(set(map(frozenset, clauses))):
            print(f"\n{c.FAIL}✗ No se pudo derivar la cláusula vacía → Conclusión no demostrada{c.ENDC}")
            if guardar: guardar_reporte(reporte, False)
            return False
        for c_ in new:
            if c_ not in clauses: clauses.append(c_)

# ---------------------------
# Guardar reporte
# ---------------------------
def guardar_reporte(pasos, exito):
    nombre = "reporte_resolucion.txt"
    with open(nombre, "w", encoding="utf-8") as f:
        f.write("Reporte de Inferencia por Resolución\n")
        f.write(f"Generado: {datetime.now()}\n\n")
        for p in pasos: f.write(p + "\n")
        f.write("\nResultado final:\n")
        f.write("✓ Se derivó la cláusula vacía → Conclusión demostrada\n" if exito
                else "✗ No se pudo derivar la cláusula vacía → Conclusión no demostrada\n")
    print(f"\n{c.OKGREEN}📄 Reporte guardado como 'reporte_resolucion.txt'{c.ENDC}")

# ---------------------------
# Interfaz con guía integrada
# ---------------------------
def main():
    print(f"{c.HEADER}=== Motor de Inferencia por Resolución (Entrada en FOL) ==={c.ENDC}")
    print(f"{c.OKCYAN}Guía rápida de escritura FOL:{c.ENDC}\n")
    print("""
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
""")

    base = []
    while True:
        s = input(f"  {len(base)+1}. ").strip()
        if s.lower() == "fin": break
        if s: base.append(s)

    pregunta = input(f"\n{c.OKCYAN}Pregunta (en FOL, ej: Odia(Marco,Cesar)): {c.ENDC}").strip()

    clauses = fol_a_fnc_clausulas(base, pregunta)
    print(f"\n{c.BOLD}=== Cláusulas (FNC) ==={c.ENDC}")
    for i, c_ in enumerate(clauses, 1): print(f"{i}. {c_}")

    resultado = resolucion([frozenset(c_) for c_ in clauses], verbose=True)
    print(f"\n{c.OKGREEN}Conclusión: Sí, {pregunta} ✅{c.ENDC}" if resultado
          else f"\n{c.FAIL}Conclusión: No se puede demostrar que {pregunta} ❌{c.ENDC}")

if __name__ == "__main__":
    main()
