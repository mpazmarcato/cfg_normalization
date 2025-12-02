from typing import List

Symbol = str

class Production:
    def __init__(self, lhs: Symbol, rhs: List[Symbol]):
        self.lhs =  lhs
        self.rhs = rhs

# set -> não ordenado {}
# list  -> ordenado []

class GLC:
    def __init__(self, variables : List[Symbol], alphabet: List[str], start: Symbol, productions: List[Production]):
        self.variables = variables
        self.alphabet = alphabet
        self.start = start
        self.productions = productions

def parse_set(string : str) -> List[Symbol]:
    return [v.strip() for v in string.strip().strip("{}").split(",")]

def parse_production(line: str) -> Production:
    left, right = line.split("->")
    left = left.strip()
    right = right.strip()

    return Production(Symbol(left), parse_set(right))

def create_grammar(file: str) -> GLC:
    all_productions = []
    all_variables = []
    alphabet = []
    start = ""
    with open(file, 'r') as archive:
        for line in archive:
            line = line.strip()

            if not line:
                continue

            if "->" in line:
                all_productions.append(parse_production(line))
            elif "=" in line:
                definition, new_set = line.split("=")

                definition = definition.strip().lower()

                if definition in ("variables", "variáveis", "variaveis"):
                    all_variables = parse_set(new_set)
                elif definition in ("alphabet", "alfabeto"):
                    alphabet = parse_set(new_set)
                elif definition in ("start", "inicial"):
                    start = new_set

    return GLC(all_variables, alphabet, start, all_productions)
