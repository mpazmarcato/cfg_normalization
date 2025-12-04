import sys
from cnf import convert_to_cnf
from gnf import convert_to_gnf

def main():
    if len(sys.argv) < 4:
        print("Uso: python main.py <arquivo.txt> <cnf|gnf> <saida.log>")
        return

    src = sys.argv[1]
    mode = sys.argv[2].lower()
    out = sys.argv[3]

    log = []

    if mode == "cnf":
        convert_to_cnf(src, log)
    elif mode == "gnf":
        convert_to_gnf(src, log)
    else:
        print("Modo inválido. Use cnf ou gnf.")
        return

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(log))

    print(f"Processo concluído. Log salvo em {out}")

if __name__ == "__main__":
    main()
