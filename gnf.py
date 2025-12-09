from typing import List, Dict, Set
from models import GLC, Production
from parser import create_grammar
from utils_log import log_step

from cnf import (
    remove_empty_productions,
    remove_duplicate_productions,
    remove_unit_productions,
    convert_to_cnf,
)

Symbol = str

# ------------------ Funções auxiliares ------------------

def rename_variables_to_Ai(glc: GLC):
    """Renomeia variáveis para A1, A2, A3, ..."""
    orig_vars = list(glc.variables)
    if glc.start in orig_vars:
        orig_vars.remove(glc.start)
    ordered = [glc.start] + orig_vars
    Ai_names = [f"A{i+1}" for i in range(len(ordered))]
    original_to_Ai = {orig: Ai for orig, Ai in zip(ordered, Ai_names)}
    Ai_to_original = {Ai: orig for orig, Ai in original_to_Ai.items()}
    new_prods = []
    for p in glc.productions:
        lhs = original_to_Ai.get(p.lhs, p.lhs)
        rhs = [original_to_Ai.get(sym, sym) for sym in p.rhs]
        new_prods.append(Production(lhs, rhs))
    return GLC(Ai_names, list(glc.alphabet), original_to_Ai[glc.start], new_prods), original_to_Ai, Ai_to_original


def substitute_Aj_into_Ai(productions: List[Production], Ai: Symbol, Aj: Symbol) -> List[Production]:
    """Substitui Aj no início das produções de Ai"""
    new_prods: List[Production] = []
    Aj_prods = [p for p in productions if p.lhs == Aj]
    for p in productions:
        if p.lhs != Ai:
            new_prods.append(p)
            continue
        rhs = p.rhs
        if rhs and rhs[0] == Aj:
            for ajp in Aj_prods:
                new_prods.append(Production(Ai, ajp.rhs + rhs[1:]))
        else:
            new_prods.append(p)
    return remove_duplicate_productions(new_prods)


def eliminate_immediate_left_recursion(productions: List[Production], A: Symbol, existing_vars: Set[Symbol]):
    """Elimina recursão à esquerda imediata usando variável Z"""
    prods_A = [p for p in productions if p.lhs == A]
    others = [p for p in productions if p.lhs != A]

    alphas, betas = [], []
    for p in prods_A:
        if p.rhs and p.rhs[0] == A:
            alphas.append(p.rhs[1:])
        else:
            betas.append(p.rhs)

    if not alphas:
        return productions, []

    counter = 1
    while f"Z{counter}" in existing_vars:
        counter += 1
    Z = f"Z{counter}"
    existing_vars.add(Z)

    new_prods = []
    # A -> βZ | β para cada β
    for beta in betas:
        if beta == ['&']:
            new_prods.append(Production(A, [Z]))
        else:
            new_prods.append(Production(A, beta + [Z]))
            new_prods.append(Production(A, beta))
    
    # Z -> αZ | α para cada α
    for alpha in alphas:
        new_prods.append(Production(Z, alpha + [Z]))
        new_prods.append(Production(Z, alpha))

    return others + new_prods, [Z]


# ------------------ Função principal ------------------

def convert_to_gnf(src_file: str, log: List) -> GLC:
    """
    Converte gramática para Forma Normal de Greibach seguindo os passos:
    1. Converter para CNF
    2. Renomear variáveis para A1, A2, ...
    3. Eliminar recursão à esquerda
    4. Garantir que todas as produções comecem com terminal
    """
    # Passo 1: Converter para CNF primeiro
    glc = create_grammar(src_file)
    log_step(log, "Gramática Original", glc)
    
    cnf_glc = convert_to_cnf(src_file, [])  # Converte para CNF
    log_step(log, "Após conversão para CNF", cnf_glc)

    # Passo 2: Renomear variáveis para A1, A2, A3, ...
    renamed_glc, _, _ = rename_variables_to_Ai(cnf_glc)
    log_step(log, "Após renomear variáveis para A1..An", renamed_glc)

    # Passo 3: Eliminar recursão à esquerda
    productions = list(renamed_glc.productions)
    Ai_vars = list(renamed_glc.variables)
    existing_vars = set(Ai_vars)
    z_vars = []

    for i, Ai in enumerate(Ai_vars):
        # Substitui Aj em Ai para j < i
        for j in range(i):
            Aj = Ai_vars[j]
            productions = substitute_Aj_into_Ai(productions, Ai, Aj)
            log_step(log, f"Substituindo {Aj} em {Ai}", 
                    GLC(Ai_vars + z_vars, renamed_glc.alphabet, renamed_glc.start, productions))
        
        # Elimina recursão à esquerda imediata em Ai
        productions, new_vars = eliminate_immediate_left_recursion(productions, Ai, existing_vars)
        if new_vars:
            z_vars.extend(new_vars)
            log_step(log, f"Eliminada recursão à esquerda em {Ai}, criadas: {', '.join(new_vars)}",
                     GLC(Ai_vars + z_vars, renamed_glc.alphabet, renamed_glc.start, productions))

    log_step(log, "Após eliminar toda recursão à esquerda", 
             GLC(Ai_vars + z_vars, renamed_glc.alphabet, renamed_glc.start, productions))

    # Passo 4: Converter para GNF
    # Processa variáveis em ordem reversa (An, An-1, ..., A1)
    all_vars = Ai_vars + z_vars
    alphabet = set(renamed_glc.alphabet)
    
    for i in range(len(Ai_vars) - 1, -1, -1):
        Ai = Ai_vars[i]
        Ai_prods = [p for p in productions if p.lhs == Ai]
        
        # Verifica se Ai já está em GNF
        is_gnf = all(p.rhs and p.rhs[0] in alphabet for p in Ai_prods)
        
        if is_gnf:
            # Substitui Ai em todas as variáveis Aj onde j < i
            for j in range(i):
                Aj = Ai_vars[j]
                productions = substitute_Aj_into_Ai(productions, Aj, Ai)
            
            # Substitui Ai em todas as variáveis Z
            for z_var in z_vars:
                productions = substitute_Aj_into_Ai(productions, z_var, Ai)
            
            log_step(log, f"Substituindo {Ai} (em GNF) nas outras variáveis", 
                     GLC(all_vars, renamed_glc.alphabet, renamed_glc.start, productions))
    
    # Remove produções epsilon se houver
    productions = [p for p in productions if p.rhs != ['&']]
    productions = remove_duplicate_productions(productions)
    
    final_glc = GLC(all_vars, renamed_glc.alphabet, renamed_glc.start, productions)
    log_step(log, "GNF final", final_glc)
    return final_glc