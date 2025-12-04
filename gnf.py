"""
elimina ε-produções

elimina unitárias

elimina inúteis

ordena variáveis

remove recursão à esquerda imediata

transforma produções para começar com terminal

expande lhs < rhs conforme índice

cria log detalhado
"""

from models import GLC, Production
from utils_log import log_step
from parser import create_grammar

# Etapas comuns: remoção de ε, unitárias, inúteis (mesmas unções  do CNF)

def remove_left_recursion(A, rhs_list, variables, log):
    """
    Recebe todas as produções de A:
        A -> A α
        A -> β
    Retorna:
        A -> β A'
        A' -> α A' | ε
    """
    recursive = []
    non_recursive = []

    for rhs in rhs_list:
        if rhs and rhs[0] == A:
            recursive.append(rhs[1:])
        else:
            non_recursive.append(rhs)

    if not recursive:
        return rhs_list, None

    # criar novo A'
    A_prime = f"{A}_R"
    idx = 1
    while A_prime in variables:
        A_prime = f"{A}_R{idx}"
        idx += 1

    new_A = []
    for beta in non_recursive:
        new_A.append(beta + [A_prime])

    new_Aprime = []
    for alpha in recursive:
        new_Aprime.append(alpha + [A_prime])
    new_Aprime.append(["&"])

    log.append(f"Eliminação de recursão à esquerda: {A} → {A_prime}\n")

    return new_A, (A_prime, new_Aprime)