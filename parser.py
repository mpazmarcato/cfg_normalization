from models import Production, GLC

def parse_set(string: str) -> List[Symbol]:
    s = string.strip()
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
    else:
        inner = s
    if not inner:
        return []
    return [v.strip() for v in inner.split(",") if v.strip()]


def parse_production(line: str):
    left, right = line.split("->", 1)
    left = left.strip()
    right = right.strip()

    alternatives = []
    if '|' in right:
        alternatives = [p.strip() for p in right.split('|') if p.strip()]
    elif right.startswith('{') and right.endswith('}'):
        alternatives = parse_set(right)
    elif ',' in right and not (right.startswith('{') or right.endswith('}')):
        alternatives = [p.strip() for p in right.split(',') if p.strip()]
    else:
        alternatives = [right]

    prods = []
    for alt in alternatives:
        if alt in ('&', 'ε'):
            symbols = ['&']
        else:
            compact = ''.join(ch for ch in alt if ch not in ' {}')
            symbols = [c for c in compact]
        prods.append(Production(Symbol(left), symbols))

    return prods


def create_grammar(file: str) -> GLC:
    all_productions: List[Production] = []
    all_variables: List[Symbol] = []
    alphabet: List[str] = []
    start: Symbol = ""

    with open(file, 'r', encoding='utf-8') as archive:
        for line in archive:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if "->" in line:
                parsed = parse_production(line)
                all_productions.extend(parsed)
            elif "=" in line:
                definition, new_set = line.split("=", 1)
                definition = definition.strip().lower()
                new_set = new_set.strip()

                if definition in ("variables", "variáveis", "variaveis"):
                    all_variables = parse_set(new_set)
                elif definition in ("alphabet", "alfabeto"):
                    alphabet = parse_set(new_set)
                elif definition in ("start", "inicial"):
                    parsed = parse_set(new_set)
                    if parsed:
                        start = parsed[0]
                    else:
                        start = new_set.strip().strip('{}').strip()

    # para gramáticas reduzidas
    if not all_variables:
        seen = []
        for p in all_productions:
            if p.lhs not in seen:
                seen.append(p.lhs)
        all_variables = seen

    if not alphabet:
        vars_set = set(all_variables)
        terms = set()
        for p in all_productions:
            for s in p.rhs:
                if s == '&':
                    continue
                if s not in vars_set:
                    terms.add(s)
        alphabet = sorted(list(terms))

    if not start:
        if all_productions:
            start = all_productions[0].lhs

    return GLC(all_variables, alphabet, start, all_productions)
