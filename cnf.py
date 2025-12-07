"""
Módulo responsável pela conversão de uma GLC para a Forma Normal de Chomsky (CNF).
Realiza as etapas:
1. Simplificação (Vazias, Unitárias, Inúteis)
2. Isolamento de terminais em produções mistas
3. Binarização de produções longas
"""

from models import GLC, Production
from parser import create_grammar
from utils_log import log_step
from itertools import combinations

Symbol = str

def convert_to_cnf(src_file: str, log: list):
    """
    Controlador principal que lê o arquivo, aplica as transformações CNF
    e registra os passos no log.
    
    Args:
        src_file (str): Caminho do arquivo de entrada.
        log (list): Lista para armazenar o log de execução.
    """
    
    glc = create_grammar(src_file)
    log_step(log, "Gramática Original", glc)

    new_prods = remove_empty_productions(glc.productions)
    glc.productions = remove_duplicate_productions(new_prods)
    
    log_step(log, "Após remoção de produções vazias", glc)

    glc = remove_unit_productions(glc)
    log_step(log, "Após remoção de produções unitárias", glc)

    glc = remove_useless_symbols(glc)
    log_step(log, "Após remoção de símbolos inúteis", glc)

    glc = convert_terminals_and_binarize(glc)
    log_step(log, "Forma Normal de Chomsky (Final)", glc)


def remove_empty_productions(productions):

    nullable = []

    for p in productions:
        if p.is_epsilon():
            nullable.append(p.lhs)
    
    changed = True
    while changed:
        changed = False
        for p in productions:
            if all(sym in nullable for sym in p.rhs):
                if p.lhs not in nullable:
                    nullable.append(p.lhs)
                    changed = True
    
    new_productions = []

    for p in productions:
        rhs = p.rhs
        nullable_positions = [i for i, s in enumerate(rhs) if s in nullable]

        for r in range(1, len(nullable_positions) + 1):
            for cm in combinations(nullable_positions, r):
                new_rhs = [rhs[i] for i in range(len(rhs)) if i not in cm]

                if new_rhs:
                    new_productions.append(
                        Production(p.lhs, new_rhs)
                    )
                else:
                    new_productions.append(
                        Production(p.lhs, ["&"])
                    )
        
    final_productions = []

    for p in productions:
        if not p.is_epsilon():
            final_productions.append(
                Production(p.lhs, list(p.rhs))
            )

    final_productions.extend(new_productions)

    return final_productions

def remove_duplicate_productions(productions):
    seen = set()
    unique = []

    for p in productions:
        key = (p.lhs, tuple(p.rhs))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def remove_unit_productions(glc: GLC) -> GLC:
    """
    Elimina produções unitárias do tipo A -> B.
    Substitui pela regra de produção de B.
    """
    
    dependencies = {v: set() for v in glc.variables}
    
    for p in glc.productions:
        if p.is_unit():
            dependencies[p.lhs].add(p.rhs[0])

    final_unit_reach = {v: {v} for v in glc.variables}
    
    for v in glc.variables:
        # BFS
        queue = [v]
        visited = {v}
        while queue:
            curr = queue.pop(0)
            if curr != v:
                final_unit_reach[v].add(curr)
            
            if curr in dependencies:
                for neighbor in dependencies[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

    new_productions = []
    
    # Coletar todas as produções NÃO unitárias
    non_unit_productions = []
    for p in glc.productions:
        if not p.is_unit():
            non_unit_productions.append(p)

    for A in glc.variables:
        reachable_vars = final_unit_reach.get(A, set())
        for B in reachable_vars:
            for p in non_unit_productions:
                if p.lhs == B:
                    new_productions.append(Production(A, list(p.rhs)))

    return GLC(glc.variables, glc.alphabet, glc.start, remove_duplicate_productions(new_productions))


def remove_useless_symbols(glc: GLC) -> GLC:
    """
    Elimina símbolos inúteis em duas etapas:
    1. Variáveis que geram terminais (Generating).
    2. Variáveis alcançáveis a partir de S (Reachable).
    """
    generating = set(glc.alphabet) 
    generating.add('&') 

    changed = True
    while changed:
        changed = False
        for p in glc.productions:
            if p.lhs not in generating:
                if all(s in generating for s in p.rhs):
                    generating.add(p.lhs)
                    changed = True
    
    step1_productions = []
    for p in glc.productions:
        if p.lhs in generating:
            if all(s in generating for s in p.rhs):
                step1_productions.append(p)
                
    reachable = {glc.start}
    changed = True
    while changed:
        changed = False
        for p in step1_productions:
            if p.lhs in reachable:
                for s in p.rhs:
                    if s not in reachable:
                        reachable.add(s)
                        changed = True

    final_productions = []
    final_vars = set()
    final_terms = set()

    for p in step1_productions:
        if p.lhs in reachable:
            if all(s in reachable or s in glc.alphabet or s == '&' for s in p.rhs):
                final_productions.append(p)
                final_vars.add(p.lhs)
                for s in p.rhs:
                    if s in glc.variables and s in reachable:
                        final_vars.add(s)
                    elif s in glc.alphabet:
                        final_terms.add(s)

    return GLC(sorted(list(final_vars)), sorted(list(final_terms)), glc.start, final_productions)


def convert_terminals_and_binarize(glc: GLC) -> GLC:
    """
    Aplica as regras finais de CNF:
    1. Corpos com tamanho >= 2 devem ser compostos apenas por variáveis.
    2. Corpos com tamanho > 2 devem ser quebrados (binarização).
    """
    productions = glc.productions
    variables = set(glc.variables)
    new_productions = []
    
    term_to_var = {}
    
    new_var_counter = 1

    def get_new_var_name(prefix="X"):
        nonlocal new_var_counter
        while True:
            name = f"{prefix}{new_var_counter}"
            if name not in variables:
                variables.add(name)
                new_var_counter += 1
                return name
            new_var_counter += 1

    temp_productions = []
    
    for p in productions:
        rhs = p.rhs
        
        if len(rhs) == 1:
            temp_productions.append(p)
            continue
            
        new_rhs = []
        for s in rhs:
            if s in glc.alphabet:
                if s in term_to_var:
                    t_var = term_to_var[s]
                else:
                    t_var = get_new_var_name("T_")
                    term_to_var[s] = t_var
                    new_productions.append(Production(t_var, [s]))
                
                new_rhs.append(t_var)
            else:
                new_rhs.append(s)
        
        temp_productions.append(Production(p.lhs, new_rhs))

    final_productions_list = list(new_productions) 
    
    for p in temp_productions:
        rhs = p.rhs
        
        if len(rhs) <= 2:
            final_productions_list.append(p)
        else:
            current_lhs = p.lhs
            current_rhs = rhs
            
            while len(current_rhs) > 2:
                left_sym = current_rhs[0]
                rest = current_rhs[1:]
                
                new_var = get_new_var_name("C_") 
                
                final_productions_list.append(Production(current_lhs, [left_sym, new_var]))
                
                current_lhs = new_var
                current_rhs = rest
            
            final_productions_list.append(Production(current_lhs, current_rhs))

    return GLC(
        sorted(list(variables)), 
        glc.alphabet, 
        glc.start, 
        final_productions_list
    )
