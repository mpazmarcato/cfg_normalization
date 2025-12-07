# Conversão para Forma Normal de Chomsky (CNF)

## Visão Geral

Este documento explica a implementação do algoritmo de conversão de uma **Gramática Livre de Contexto (GLC)** para a **Forma Normal de Chomsky (CNF)** contido no arquivo `cnf.py`.

A **CNF** é uma forma padronizada onde todas as regras de produção seguem um de dois formatos:
- **A → BC** (uma variável gera exatamente duas variáveis)
- **A → a** (uma variável gera exatamente um terminal)

## Objetivo

Transformar qualquer GLC em uma forma normalizada que:
- Facilita análise sintática
- Permite aplicação de algoritmos como CYK (Cocke-Younger-Kasami)
- Mantém a linguagem gerada pela gramática original

---

## Pipeline de Transformação

A conversão é realizada em **5 etapas sequenciais**, orquestradas pela função `convert_to_cnf()`:

```
Gramática Original
       ↓
[1] Remoção de Produções Vazias
       ↓
[2] Remoção de Produções Unitárias
       ↓
[3] Remoção de Símbolos Inúteis
       ↓
[4] Isolamento de Terminais
       ↓
[5] Binarização
       ↓
    CNF Final
```

---

## Etapas Detalhadas

### Remoção de Produções Vazias (ε-livre)

**Função:** `remove_empty_productions(productions)`

#### Problema
Produções do tipo `A → &` (epsilon/vazio) violam a CNF.

#### Solução
1. **Identificar variáveis anuláveis**: Variáveis que podem derivar vazio (direta ou indiretamente)
2. **Expandir combinações**: Para cada produção que contém variáveis anuláveis, gerar todas as combinações de presença/ausência dessas variáveis

#### Exemplo
```
Entrada:
S → AB
A → a | &
B → b

Nullable: {A}

Saída:
S → AB | B    (A presente e ausente)
A → a
B → b
```

#### Algoritmo
```python
# 1. Identificar anuláveis diretas
nullable = {variáveis que produzem &}

# 2. Fechamento transitivo
while mudanças:
    para cada produção A → α:
        se todos(α) ∈ nullable:
            adicionar A ao nullable

# 3. Expandir combinações
para cada produção A → X₁X₂...Xₙ:
    para cada combinação de Xᵢ ∈ nullable:
        adicionar A → (versão sem os Xᵢ escolhidos)
```

**Estrutura de dados chave:** `itertools.combinations` para gerar subconjuntos

---

### Remoção de Produções Unitárias (A → B)

**Função:** `remove_unit_productions(glc)`

#### Problema
Produções onde uma variável apenas "chama" outra variável (A → B) são redundantes.

#### Solução
Substituir produções unitárias pelas produções finais que elas alcançam.

#### Exemplo
```
Entrada:
S → A
A → B
B → a | b

Saída:
S → a | b    (eliminou intermediários)
A → a | b
B → a | b
```

#### Algoritmo (Grafos + BFS)
```python
# 1. Construir grafo de dependências
dependencies = {A: {B} se existe A → B}

# 2. Fecho transitivo via BFS
para cada variável V:
    alcançáveis[V] = BFS(V, grafo de dependencies)

# 3. Copiar produções não-unitárias
para cada variável A:
    para cada B ∈ alcançáveis[A]:
        copiar todas produções não-unitárias de B para A
```

**Estrutura de dados chave:** Dicionário de adjacência + fila BFS

---

### Remoção de Símbolos Inúteis

**Função:** `remove_useless_symbols(glc)`

#### Problema
Símbolos que nunca podem aparecer em derivações válidas (inférteis ou inacessíveis).

#### Solução
Aplicar dois filtros sequenciais:

##### **Filtro 1: Generating (Férteis)**
Variáveis que conseguem gerar pelo menos uma string de terminais.

```python
generating = alfabeto  # Terminais geram a si mesmos
while mudanças:
    para cada produção A → α:
        se todos(α) ∈ generating:
            adicionar A ao generating
```

##### **Filtro 2: Reachable (Acessíveis)**
Símbolos alcançáveis a partir do símbolo inicial.

```python
reachable = {Start}
while mudanças:
    para cada produção A → α onde A ∈ reachable:
        adicionar todos(α) ao reachable
```

#### Exemplo
```
Entrada:
S → AB
A → a
B → C    # C é infértil (não gera terminais)
C → C

Saída:
S → (removido, pois B não é fértil)
A → a
```

---

### Isolamento de Terminais

**Função:** `convert_terminals_and_binarize(glc)` (Parte 1)

#### Problema
Regras mistas como `A → aB` ou `A → aBc` não são permitidas em CNF.

#### Solução
Criar variáveis "carteiras" para terminais que aparecem em produções com tamanho ≥ 2.

#### Exemplo
```
Entrada:
S → aB
A → abc

Saída:
S → T_a B
A → T_a T_b T_c
T_a → a
T_b → b
T_c → c
```

#### Algoritmo
```python
term_to_var = {}  # Mapa: terminal → variável criada

para cada produção A → X₁X₂...Xₙ onde n ≥ 2:
    para cada símbolo Xᵢ:
        se Xᵢ é terminal:
            se Xᵢ não tem variável:
                criar T_Xᵢ → Xᵢ
            substituir Xᵢ por T_Xᵢ
```

**Nota:** Terminais em produções de tamanho 1 (como `A → a`) permanecem intactos.

---

### Binarização

**Função:** `convert_terminals_and_binarize(glc)` (Parte 2)

#### Problema
Produções com mais de 2 símbolos à direita (A → BCD) violam a CNF.

#### Solução
Quebrar recursivamente usando variáveis auxiliares.

#### Exemplo
```
Entrada:
S → ABCD

Saída:
S → A C_1
C_1 → B C_2
C_2 → C D
```

#### Algoritmo
```python
para cada produção A → X₁X₂...Xₙ onde n > 2:
    atual_lhs = A
    atual_rhs = [X₁, X₂, ..., Xₙ]
    
    enquanto len(atual_rhs) > 2:
        criar nova variável C_i
        adicionar: atual_lhs → X₁ C_i
        atual_lhs = C_i
        atual_rhs = [X₂, ..., Xₙ]
    
    adicionar: atual_lhs → últimos 2 símbolos
```

**Estrutura de dados chave:** Loop while + lista de símbolos

---
