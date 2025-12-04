from typing import List

Symbol = str

class Production:
    def __init__(self, lhs: Symbol, rhs: List[Symbol]):
        self.lhs =  lhs
        self.rhs = rhs

    def __repr__(self):
        if not self.rhs or (len(self.rhs) == 1 and self.rhs[0] == "&"):
            rhs_str = "&"
        else:
            rhs_str = ''.join(self.rhs)
        return f"{self.lhs} -> {rhs_str}"
    
    def is_epsilon(self):
        return len(self.rhs) == 1 and self.rhs[0] == "&"
    
    def is_unit(self):
        return len(self.rhs) == 1 and self.rhs[0].isupper()

# set -> não ordenado {}
# list  -> ordenado []

class GLC:
    def __init__(self, variables : List[Symbol], alphabet: List[str], start: Symbol, productions: List[Production]):
        self.variables = variables
        self.alphabet = alphabet
        self.start = start
        self.productions = productions

    def copy(self):
        return GLC(
            list(self.variables),
            list(self.alphabet),
            self.start,
            [Production(p.lhs, list(p.rhs)) for p in self.productions]
        )

    def __repr__(self):
        lines = [
            f"Start: {self.start}",
            f"Variables: {self.variables}",
            f"Alphabet: {self.alphabet}",
            "Productions:"
        ]
        for p in self.productions:
            lines.append("  " + repr(p))
        return "\n".join(lines)