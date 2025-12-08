"""
Módulo clássico para conversão de uma GLC (Gramática Livre de Contexto)
para a Forma Normal de Greibach (GNF).

Implementação baseada nos teoremas canônicos e no algoritmo que renomeia
variáveis para A1..An e, para i = 1..n, substitui produções Ai -> Aj α (com j < i)
e elimina recursão à esquerda imediata em Ai, introduzindo variáveis Zk quando necessário.

O módulo reaproveita as funções de pré-processamento do cnf.py
(remoção de ε-productions, unitárias e símbolos inúteis) e registra
os passos usando utils_log.log_step.

Convenção: ε é representado por '&'.
"""

from typing import List, Dict, Set, Tuple
from models import GLC, Production
from parser import create_grammar
from utils_log import log_step

from cnf import (
    remove_empty_productions,
    remove_duplicate_productions,
    remove_unit_productions,
    remove_useless_symbols,
)

Symbol = str

# Funções auxiliares para GNF

def rename_variables_to_Ai(glc: GLC) -> Tuple[GLC, Dict[Symbol, Symbol], Dict[Symbol, Symbol]]:
    """
    Renomeia as variáveis de glc.variables para A1..An, garantindo A1 = start.
    Retorna (novo_glc, original_to_Ai, Ai_to_original).
    """
    orig_vars = list(glc.variables)
    if glc.start in orig_vars:
        orig_vars.remove(glc.start)
    ordered = [glc.start] + orig_vars

    Ai_names = [f"A{i+1}" for i in range(len(ordered))]
    original_to_Ai = {orig: Ai for orig, Ai in zip(ordered, Ai_names)}
    Ai_to_original = {Ai: orig for orig, Ai in original_to_Ai.items()}

    new_prods: List[Production] = []
    for p in glc.productions:
        lhs = original_to_Ai.get(p.lhs, p.lhs)
        rhs = [original_to_Ai.get(sym, sym) for sym in p.rhs]
        new_prods.append(Production(lhs, rhs))

    new_vars = Ai_names
    new_start = original_to_Ai[glc.start]
    new_alphabet = list(glc.alphabet)

    return GLC(new_vars, new_alphabet, new_start, new_prods), original_to_Ai, Ai_to_original


def substitute_Aj_into_Ai(productions: List[Production], Ai: Symbol, Aj: Symbol) -> List[Production]:
    """
    Substitui em todas as produções com cabeça Ai, aquelas cujo RHS começa com Aj,
    pela expansão usando as produções de Aj.
    """
    new_prods: List[Production] = []
    Aj_prods = [p for p in productions if p.lhs == Aj]

    for p in productions:
        if p.lhs != Ai:
            new_prods.append(p)
            continue

        rhs = p.rhs
        if len(rhs) > 0 and rhs[0] == Aj:
            for ajp in Aj_prods:
                new_rhs = list(ajp.rhs) + list(rhs[1:])
                new_prods.append(Production(Ai, new_rhs))
        else:
            new_prods.append(p)

    return remove_duplicate_productions(new_prods)


def immediate_left_recursion_elimination_for_A(productions: List[Production], A: Symbol, new_var_generator) -> Tuple[List[Production], List[Symbol]]:
    """
    Elimina recursão à esquerda imediata nas produções com cabeça A, se existir.
    Retorna (productions_modificadas, lista_de_novas_variaveis_criadas).
    """
    prods_A = [p for p in productions if p.lhs == A]
    others = [p for p in productions if p.lhs != A]

    alphas: List[List[Symbol]] = []
    betas: List[List[Symbol]] = []

    for p in prods_A:
        if len(p.rhs) > 0 and p.rhs[0] == A:
            alphas.append(p.rhs[1:])
        else:
            betas.append(p.rhs)

    if not alphas:
        return productions, []

    Z = new_var_generator(A)

    new_prods: List[Production] = []
    for beta in betas:
        if len(beta) == 1 and beta[0] == '&':
            new_prods.append(Production(A, [Z]))
        else:
            new_prods.append(Production(A, list(beta) + [Z]))

    for alpha in alphas:
        new_prods.append(Production(Z, list(alpha) + [Z]))

    new_prods.append(Production(Z, ['&']))

    combined = others + new_prods
    combined = remove_duplicate_productions(combined)

    return combined, [Z]


def new_var_generator_factory(existing_vars: Set[Symbol]):
    counter = 1

    def gen(_: Symbol) -> Symbol:
        nonlocal counter
        while True:
            name = f"Z{counter}"
            counter += 1
            if name not in existing_vars:
                existing_vars.add(name)
                return name
    return gen

# Algoritmo clássico 

def convert_to_gnf(src_file: str, log: List) -> GLC:
    """
    1) Ler e logar gramática original
    2) Pré-simplificações 
    3) Renomear variáveis para A1...An com A1 = S
    4) Para i = 1..n: aplicar teoremas
    5) Garantir que todas as produções começam por terminal 
    6) Construir GLC final
    """
    glc = create_grammar(src_file)
    log_step(log, "Gramática Original", glc)
 
    prods = remove_empty_productions(glc.productions)
    prods = remove_duplicate_productions(prods)
    glc.productions = prods
    log_step(log, "Após remoção de produções vazias", glc)

    glc = remove_unit_productions(glc)
    log_step(log, "Após remoção de produções unitárias", glc)

    glc = remove_useless_symbols(glc)
    log_step(log, "Após remoção de símbolos inúteis", glc)

    renamed_glc, orig_to_Ai, Ai_to_orig = rename_variables_to_Ai(glc)
    log_step(log, "Após renomear variáveis para A1..An (pré-processamento)", renamed_glc)

    productions: List[Production] = list(renamed_glc.productions)
    Ai_vars: List[Symbol] = list(renamed_glc.variables)
    existing = set(Ai_vars)
    new_var_gen = new_var_generator_factory(existing)

    i = 0
    while i < len(Ai_vars):
        Ai = Ai_vars[i]
        # substituir produções Ai -> Aj α para todo j < i
        for j in range(i):
            Aj = Ai_vars[j]
            productions = substitute_Aj_into_Ai(productions, Ai, Aj)
            log_step(log, f"Substituições em {Ai} substituindo {Aj} (j < i)", GLC(Ai_vars, renamed_glc.alphabet, renamed_glc.start, productions))

        productions, new_vars = immediate_left_recursion_elimination_for_A(productions, Ai, new_var_gen)
        if new_vars:
            for idx, z in enumerate(new_vars, start=1):
                Ai_vars.insert(i + idx, z)
            log_step(log, f"Eliminada recursão à esquerda imediata em {Ai}, criadas: {', '.join(new_vars)}", GLC(Ai_vars, renamed_glc.alphabet, renamed_glc.start, productions))

        i += 1
    
    grouped: Dict[Symbol, List[List[Symbol]]] = {v: [] for v in Ai_vars}
    for p in productions:
        grouped.setdefault(p.lhs, []).append(p.rhs)

    changed = True
    while changed:
        changed = False
        for A in list(grouped.keys()):
            new_list: List[List[Symbol]] = []
            for rhs in grouped.get(A, []):
                if not rhs:
                    continue
                first = rhs[0]
                if first in renamed_glc.alphabet or (len(rhs) == 1 and rhs[0] == '&'):
                    new_list.append(rhs)
                    continue

                if first in grouped:
                    for gamma in grouped[first]:
                        new_list.append(gamma + rhs[1:])
                        changed = True
                else:
                    new_list.append(rhs)

            seen = set()
            deduped: List[List[Symbol]] = []
            for r in new_list:
                key = tuple(r)
                if key not in seen:
                    seen.add(key)
                    deduped.append(r)
            grouped[A] = deduped

    final_prods: List[Production] = []
    for A in grouped:
        for rhs in grouped[A]:
            if len(rhs) == 1 and rhs[0] == '&' and A != renamed_glc.start:
                continue
            final_prods.append(Production(A, rhs))

    final_prods = remove_duplicate_productions(final_prods)

    final_vars = sorted(list({p.lhs for p in final_prods}))
    final_alphabet = renamed_glc.alphabet
    final_start = renamed_glc.start

    final_glc = GLC(final_vars, final_alphabet, final_start, final_prods)
    log_step(log, "GNF (clássico) - Resultado final", final_glc)

    return final_glc
