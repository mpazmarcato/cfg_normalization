# GLC Normalizer

Ferramenta modular para converter Gramáticas Livre de Contexto (GLC)
- Para Forma Normal de Chomsky (CNF)

- Para Forma Normal de Greibach (GNF)

Projeto desenvolvido em Python, com suporte a:
- Arquivos .txt reduzidos

- Arquivos .txt completos (Variáveis, Alfabeto, Inicial, Regras)

- Símbolo vazio: & ou ε

- Log completo passo a passo gerado automaticamente

## Estrutura do Projeto
```Bash
glc_normalizer/
│
├── main.py
├── parser.py
├── models.py
├── utils_log.py
├── utils_debug.py
├── cnf.py
├── gnf.py
├── README.md
└── exemplos/
     ├── GLC-Reduzida.txt
     └── GLC-Completa.txt
```

## Como executar
Para CNF

```Bash
python main.py GLC-Reduzida.txt cnf reduzida.log
python main.py GLC-Completa.txt cnf completa.log
```

Para GNF

```Bash
python main.py GLC-Reduzida.txt gnf saida.log
python main.py GLC-Completa.txt gnf saida.log
```

## Formatos aceitos
- Formato reduzido
```Bash
S -> A01BC
S -> &
A -> 01
A -> 1B1
...
```

- Formato completo
```Bash
Variaveis = {S, A, B, C}
Alfabeto = {0, 1, 2}
Inicial = S
Regras:
S -> A01BC
S -> &
...
```

## Saída (arquivo .log)

O arquivo de log registra:

- Gramática lida

Cada etapa:

- Remoção de ε-produções

- Remoção de unitárias

- Remoção de símbolos inúteis

- Separação de terminais

- Binarização

- Ordenação de variáveis (GNF)

- Expansões

- Remoção de recursão à esquerda

- Garantir terminal no início das regras

- Gramática final

# Testes

Rode os testes no terminal

```bash
$ python -m unittest discover tests -v
```

![testes executados](/doc/images/image.png)
