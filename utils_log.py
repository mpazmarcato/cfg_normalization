def grammar_as_text(glc):
    lines = []
    lines.append(f"Start: {glc.start}")
    lines.append("Variables: {" + ", ".join(glc.variables) + "}")
    lines.append("Alphabet: {" + ", ".join(glc.alphabet) + "}")
    lines.append("Productions:")
    for p in glc.productions:
        lines.append("  " + repr(p))
    return "\n".join(lines)

def log_step(log, title, glc):
    log.append("==== " + title + " ====")
    log.append(grammar_as_text(glc))
    log.append("")
