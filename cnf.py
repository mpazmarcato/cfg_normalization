from models import Production
from itertools import combinations

Symbol = str

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
