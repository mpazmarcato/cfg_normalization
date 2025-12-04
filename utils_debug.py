from models import GLC

def print_productions(glc: GLC):
    print("Produções:")
    for p in glc.productions:
        print(" ", p)

def print_grammar(glc: GLC, fname: str = None):
    header = f"--- Gramática" + (f" lida de: {fname} ---" if fname else " ---")
    print("\n" + header)
    print("Alfabeto:", glc.alphabet)
    print("Inicial:", glc.start)
    print("Variáveis:", glc.variables)
    print_productions(glc)
