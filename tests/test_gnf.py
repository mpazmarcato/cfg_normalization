import unittest
import os
from models import GLC, Production
from gnf import (
    rename_variables_to_Ai,
    substitute_Aj_into_Ai,
    immediate_left_recursion_elimination_for_A,
    new_var_generator_factory,
    convert_to_gnf
)

class TestGNF(unittest.TestCase):

    def setUp(self):
        """Métodos auxiliares para criação de produções."""
        self.temp_file = "temp_grammar_gnf_test.txt"

    def tearDown(self):
        """Limpeza de arquivos temporários."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def create_prod(self, lhs, rhs_list):
        """Ajuda a criar produções. rhs_list deve ser uma lista de strings."""
        return Production(lhs, rhs_list)

    def prods_to_set(self, productions):
        """Converte lista de produções em strings para fácil comparação."""
        return {str(p) for p in productions}

    def write_grammar_file(self, content):
        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write(content)

    # =================================================================
    # 1. TESTES DE RENOMEAÇÃO (A1, A2...)
    # =================================================================
    def test_rename_variables_simple(self):
        p1 = self.create_prod('S', ['A'])
        p2 = self.create_prod('A', ['a'])
        glc = GLC(['S', 'A'], ['a'], 'S', [p1, p2])

        new_glc, map_orig_Ai, map_Ai_orig = rename_variables_to_Ai(glc)
        
        self.assertEqual(map_orig_Ai['S'], 'A1')
        self.assertEqual(map_orig_Ai['A'], 'A2')
        
        res_set = self.prods_to_set(new_glc.productions)
        self.assertIn("A1 -> A2", res_set) # S -> A virou A1 -> A2
        self.assertIn("A2 -> a", res_set)  # A -> a virou A2 -> a

    # =================================================================
    # 2. TESTES DE SUBSTITUIÇÃO (Aj em Ai)
    # =================================================================
    def test_substitute_Aj_into_Ai(self):
        
        prods = [
            self.create_prod('A1', ['A2', 'b']),
            self.create_prod('A2', ['a']),
            self.create_prod('A2', ['c']),
            self.create_prod('A3', ['d']) # Controle: não deve mudar
        ]

        new_prods = substitute_Aj_into_Ai(prods, 'A1', 'A2')
        res_set = self.prods_to_set(new_prods)

        self.assertIn("A1 -> ab", res_set)
        self.assertIn("A1 -> cb", res_set)
        self.assertNotIn("A1 -> A2b", res_set) # Ajustado para A2b
        self.assertIn("A2 -> a", res_set) 
        self.assertIn("A3 -> d", res_set)
    
    # =================================================================
    # 3. TESTES DE ELIMINAÇÃO DE RECURSÃO À ESQUERDA IMEDIATA
    # =================================================================
    def test_immediate_recursion(self):
        
        prods = [
            self.create_prod('A', ['A', 'a']),
            self.create_prod('A', ['b'])
        ]
        
        existing_vars = {'A'}
        gen = new_var_generator_factory(existing_vars)
        
        new_prods, created_vars = immediate_left_recursion_elimination_for_A(prods, 'A', gen)
        res_set = self.prods_to_set(new_prods)
        
        self.assertEqual(len(created_vars), 1)
        Z = created_vars[0] # Deve ser Z1
        
        self.assertIn(f"A -> b{Z}", res_set)   # Antes: b {Z}
        self.assertIn(f"{Z} -> a{Z}", res_set) # Antes: a {Z}
        self.assertIn(f"{Z} -> &", res_set)
        
        self.assertNotIn("A -> Aa", res_set)

    # =================================================================
    # 4. TESTES DE INTEGRAÇÃO (convert_to_gnf)
    # =================================================================
    def check_is_gnf(self, glc):
        """Valida se todas as produções começam com terminal."""
        for p in glc.productions:
            if p.is_epsilon(): 
                continue # Permite epsilon se for regra gerada/tratada
            
            first = p.rhs[0]
            self.assertIn(first, glc.alphabet, f"Produção não está em GNF: {p}")

    def test_gnf_simple_substitution(self):
        """Teste simples onde apenas substituição resolve."""
        content = """
        Variaveis = {S, A, B}
        Alfabeto = {a, b}
        Inicial = S
        Regras:
        S -> A B
        A -> a
        B -> b
        """
        self.write_grammar_file(content)
        
        log = []
        final_glc = convert_to_gnf(self.temp_file, log)
        
        res_set = self.prods_to_set(final_glc.productions)
        
        self.check_is_gnf(final_glc)
        
        found_terminal_start = any(p.rhs[0] == 'a' for p in final_glc.productions)
        self.assertTrue(found_terminal_start, "Deveria haver produção começando com 'a'")

    def test_gnf_with_recursion(self):
        """Teste com recursão à esquerda que exige criação de Z."""
        content = """
        Variaveis = {S}
        Alfabeto = {a, b}
        Inicial = S
        Regras:
        S -> S a | b
        """
        self.write_grammar_file(content)
        
        log = []
        final_glc = convert_to_gnf(self.temp_file, log)
        
        self.check_is_gnf(final_glc)
        
        self.assertTrue(len(final_glc.variables) > 1)

    def test_gnf_full_cycle(self):
        """Teste mais complexo com ciclo e recursão."""
        content = """
        Variaveis = {S, A}
        Alfabeto = {a, b}
        Inicial = S
        Regras:
        S -> A A | a
        A -> S S | b
        """
        self.write_grammar_file(content)
        
        log = []
        final_glc = convert_to_gnf(self.temp_file, log)
        
        self.check_is_gnf(final_glc)
        
        self.assertEqual(set(final_glc.alphabet), {'a', 'b'})

if __name__ == '__main__':
    unittest.main()
