# Conversão para Forma Normal de Greibach (GNF)

## Visão Geral
Este documento explica a implementação do algoritmo de conversão de uma Gramática Livre de Contexto (GLC) para a Forma Normal de Greibach (GNF) contido no arquivo `gnf.py`.

A GNF é uma forma normal restrita onde todas as regras de produção seguem o formato:

```
A → aα
```

(uma variável gera um terminal seguido por zero ou mais variáveis)

Onde:
- **a** é um terminal (símbolo do alfabeto)  
- **α** é uma sequência (possivelmente vazia) de variáveis

## Objetivo
Transformar qualquer GLC em uma forma normalizada que:
- Facilita análise sintática por métodos de pilha
- É necessária para provas teóricas sobre autômatos de pilha
- Mantém a linguagem gerada pela gramática original

## Pipeline de Transformação
A conversão é realizada em 4 etapas sequenciais, orquestradas pela função `convert_to_gnf()`:

```
Gramática Original
       ↓
[1] Converter para Forma Normal de Chomsky (CNF)
       ↓
[2] Renomear Variáveis para A1, A2, ..., An
       ↓
[3] Eliminar Recursão à Esquerda
       ↓
[4] Converter para Forma Greibach
       ↓
    GNF Final
```

---

## Etapas Detalhadas

### Etapa 1: Conversão para Forma Normal de Chomsky (CNF)
**Função:** `convert_to_cnf()` (reutilizada do módulo CNF)

**Objetivo**  
Preparar a gramática em um formato padronizado que facilita a conversão subsequente para GNF.

**Características da CNF**
- Todas as produções têm formato: `A → BC` ou `A → a`
- Elimina produções ε (vazias) e produções unitárias
- Normaliza o comprimento das produções

**Por que começar com CNF?**  
A CNF fornece uma estrutura ideal porque:
- Todas as produções têm no máximo 2 símbolos no lado direito
- As produções terminais já estão isoladas (`A → a`)
- Simplifica o processo de reordenação para GNF

---

### Etapa 2: Renomear Variáveis para A1, A2, ..., An
**Função:** `rename_variables_to_Ai(glc)`

**Problema**  
Algoritmos de conversão para GNF exigem ordenação das variáveis.

**Solução**  
Renomear todas as variáveis seguindo uma ordem canônica:

- `A1` = símbolo inicial  
- `A2, A3, ..., An` = demais variáveis em ordem alfabética

**Exemplo**

Entrada (CNF):
```
S → AB | a
A → a
B → b
```

Renomeação:
```
A1 → A2A3 | a
A2 → a
A3 → b
```

**Algoritmo (pseudocódigo)**
```python
# 1. Identificar símbolo inicial
ordered = [start_symbol] + [outras_variáveis_ordenadas]

# 2. Criar mapeamento
for i, var in enumerate(ordered, 1):
    mapeamento[var] = f"A{i}"

# 3. Aplicar mapeamento em todas as produções
```

---

### Etapa 3: Eliminar Recursão à Esquerda
**Função:** `eliminate_immediate_left_recursion()`

**Problema**  
Produções do tipo `A → Aα` (recursão direta) ou `A → Bα, B → Aβ` (recursão indireta) impedem a conversão direta para GNF.

**Solução**  
Duas estratégias combinadas:

#### 3.1 Substituição Direta
Para produções `Ai → Ajα` onde `j < i`:
- Substituir `Aj` por todas as suas produções

Pseudocódigo:
```python
# Para cada Ai:
for j in range(i):
    Aj = variáveis[j]
    # Substituir Aj no início das produções de Ai
    novas_produções = substituir(Ai, Aj, produções_de_Aj)
```

#### 3.2 Eliminação de Recursão Direta
Para produções `A → Aα`:
- Criar nova variável `Z`
- Transformar em:

```
A → βZ | β
Z → αZ | α
```

**Exemplo**

Entrada:
```
A → Aa | b
```

Saída:
```
A → bZ | b
Z → aZ | a
```

**Algoritmo (pseudocódigo)**
```python
# Separar produções recursivas e não-recursivas
alphas = []  # Para A → Aα
betas = []   # Para A → β (não recursivas)

for produção in produções_de_A:
    if produção começa com A:
        alphas.append(resto_da_produção)
    else:
        betas.append(produção)

if alphas:
    criar Z
    # A → βZ | β para cada β
    # Z → αZ | α para cada α
```

---

### Etapa 4: Converter para Forma Greibach
**Função:** Implementada no loop final de `convert_to_gnf()`

**Problema**  
As produções após a etapa 3 ainda podem começar com variáveis, não com terminais.

**Solução**  
Processar variáveis em ordem reversa (`An` até `A1`) garantindo que:
- Quando processamos `Ai`, todas as variáveis `Aj` (j > i) já estão em GNF
- Podemos substituir variáveis iniciais por produções que já começam com terminal

**Técnica Principal: Substituição Direta**
```python
# Processar do maior índice para o menor
for i de len(Ai_vars)-1 até 0:
    Ai = Ai_vars[i]

    # Se Ai já está em GNF (produções começam com terminal)
    if todas_produções_de_Ai_começam_com_terminal:
        # Substituir Ai em todas as outras variáveis
        for cada variável V que não seja Ai:
            para cada produção de V que começa com Ai:
                substituir Ai por suas produções
```

**Exemplo**

## Entrada (após etapa 3)

```
A3 → a                  # Já em GNF
A2 → A3 A3
A1 → A2 A4 | A3 A5
A4 → A3 A6
A5 → A3
A6 → a                  # Já em GNF
```

---

## Processo

### 1. A3 já está em GNF → substituir A3 em A2
Produção original:
```
A2 → A3 A3
```

Substituição:
```
A2 → a A3
```

A2 agora começa com terminal → está em GNF.

---

### 2. A2 agora em GNF → substituir A2 em A1

Produções originais:
```
A1 → A2 A4
A1 → A3 A5
```

#### Para `A1 → A2 A4`
```
A1 → a A3 A4
```

#### Para `A1 → A3 A5`
```
A1 → a A5
```

A1 agora só possui produções que começam com terminal → está em GNF.

---

### 3. Substituir A3 em A5 e A4 (completando o processo)

```
A5 → A3     →   A5 → a
A4 → A3 A6  →   A4 → a A6
```

---

## GNF Final

```
A3 → a
A6 → a
A5 → a
A2 → a A3
A4 → a A6
A1 → a A3 A4
A1 → a A5
```

Todas as produções agora estão na Forma Normal de Greibach (GNF).

---

## Estrutura do Algoritmo Completo
```python
def convert_to_gnf(src_file: str, log: List) -> GLC:
    # 1. Converter para CNF
    cnf_glc = convert_to_cnf(src_file, [])

    # 2. Renomear variáveis para A1..An
    renamed_glc, _, _ = rename_variables_to_Ai(cnf_glc)

    # 3. Eliminar recursão à esquerda
    #   3.1. Para cada i, substituir Aj (j < i) em Ai
    #   3.2. Eliminar recursão imediata em Ai

    # 4. Converter para GNF
    #   4.1. Processar variáveis em ordem reversa
    #   4.2. Garantir que cada variável tenha produções que começam com terminal
    #   4.3. Substituir variáveis iniciais por produções em GNF

    # 5. Remover produções ε e duplicadas
    # 6. Retornar gramática em GNF
```

---

## Limitações e Observações
1. **Complexidade**  
   O algoritmo tem complexidade `O(n³)` no pior caso.  
   O número de produções pode crescer exponencialmente.

2. **Produções ε**  
   Produções vazias são removidas durante a conversão.  
   A gramática resultante não gera a string vazia (a menos que seja adicionada explicitamente).

3. **Variáveis Auxiliares**  
   São criadas variáveis `Z1, Z2, ...` para eliminar recursão.  
   Essas variáveis são processadas após as variáveis originais.

4. **Unicidade da Solução**  
   A GNF resultante não é única.  
   Diferentes ordenações podem produzir diferentes GNFs, mas todas as GNFs geram a mesma linguagem.


---

## Verificação da GNF
Uma gramática está em GNF se e somente se:
- Todas as produções têm formato: `A → aα` (onde `a` é terminal e `α` é sequência de variáveis, pode ser vazia)
- Não há produções ε (exceto possivelmente do símbolo inicial)
- Não há produções unitárias

**Função de verificação (pseudocódigo)**
```python
def verificar_gnf(glc: GLC) -> bool:
    for p in glc.productions:
        if not p.rhs:  # Produção vazia
            return False
        if p.rhs[0] not in glc.alphabet:  # Não começa com terminal
            return False
    return True
```

---

## Referências Teóricas
- Teorema de Greibach: Toda GLC pode ser convertida para GNF  
- Prova de equivalência: A GNF mantém a linguagem da gramática original

**Aplicações:**
- Análise sintática descendente  
- Construção de autômatos de pilha  
- Provas de completude para linguagens livres de contexto

