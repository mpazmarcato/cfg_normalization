import unittest
from models import GLC, Production
from cnf import (
    remove_empty_productions,
    remove_unit_productions,
    remove_useless_symbols,
    convert_terminals_and_binarize,
    remove_duplicate_productions
)

class TestCNF(unittest.TestCase):

    def setUp(self):
        """Executado antes de cada teste. Ajuda a criar objetos comuns."""
        pass

    def create_prod(self, lhs, rhs_str):
        """Ajuda a criar produções rapidamente. Ex: create_prod('S', 'AB')"""
        return Production(lhs, list(rhs_str))

    def prods_to_set(self, productions):
        """Converte lista de produções em strings para fácil comparação (ignora ordem)."""
        return {str(p) for p in productions}

    # =================================================================
    # TESTES DE REMOÇÃO DE PRODUÇÕES VAZIAS (& ou ε)
    # =================================================================
    def test_remove_empty_productions_simple(self):
        
        p1 = self.create_prod('S', 'AB')
        p2 = Production('A', ['&']) 
        p3 = self.create_prod('B', 'b')
        
        input_prods = [p1, p2, p3]
        result = remove_empty_productions(input_prods)
        result_set = self.prods_to_set(result)

        self.assertIn("S -> AB", result_set)
        self.assertIn("S -> B", result_set)
        self.assertIn("B -> b", result_set)
        self.assertNotIn("A -> &", result_set)

    # =================================================================
    # TESTES DE REMOÇÃO DE UNITÁRIAS (A -> B)
    # =================================================================
    def test_remove_unit_chain(self):
        prods = [
            self.create_prod('S', 'A'),
            self.create_prod('A', 'B'),
            self.create_prod('B', 'b')
        ]
        glc = GLC(['S','A','B'], ['b'], 'S', prods)
        
        new_glc = remove_unit_productions(glc)
        res_set = self.prods_to_set(new_glc.productions)
        
        self.assertIn("S -> b", res_set)
        self.assertIn("A -> b", res_set)
        self.assertNotIn("S -> A", res_set)

    # =================================================================
    # TESTES DE SÍMBOLOS INÚTEIS
    # =================================================================
    def test_remove_useless_unreachable(self):
        prods = [
            self.create_prod('S', 'a'),
            self.create_prod('B', 'b')
        ]
        glc = GLC(['S','B'], ['a','b'], 'S', prods)
        
        new_glc = remove_useless_symbols(glc)
        res_set = self.prods_to_set(new_glc.productions)
        
        self.assertIn("S -> a", res_set)
        self.assertNotIn("B -> b", res_set)
        self.assertNotIn('B', new_glc.variables)

    def test_remove_useless_nongenerating(self):
        prods = [
            self.create_prod('S', 'A'),
            self.create_prod('A', 'aB'),
            self.create_prod('B', 'B')
        ]
        glc = GLC(['S','A','B'], ['a'], 'S', prods)
        
        new_glc = remove_useless_symbols(glc)
        self.assertEqual(len(new_glc.productions), 0)

    # =================================================================
    # TESTES DE CONVERSÃO FINAL (CNF)
    # =================================================================
    def test_convert_terminals_and_binarize(self):
        
        prods = [self.create_prod('S', 'aAB')]
        glc = GLC(['S','A','B'], ['a'], 'S', prods)
        
        final_glc = convert_terminals_and_binarize(glc)
        res_set = self.prods_to_set(final_glc.productions)
        
        for p in final_glc.productions:
            self.assertTrue(len(p.rhs) <= 2, f"Regra muito longa encontrada: {p}")
            if len(p.rhs) == 2:
                self.assertTrue(p.rhs[0].isupper() or '_' in p.rhs[0], "Corpo binário com terminal")
                self.assertTrue(p.rhs[1].isupper() or '_' in p.rhs[1], "Corpo binário com terminal")
            if len(p.rhs) == 1:
                pass


    def test_heavy_binarization(self):
        """Testa se regras muito longas são quebradas corretamente em cascata."""
        prods = [
            self.create_prod('S', 'ABCDE'),
            self.create_prod('A', 'a'), self.create_prod('B', 'b'),
            self.create_prod('C', 'c'), self.create_prod('D', 'd'),
            self.create_prod('E', 'e')
        ]
        glc = GLC(['S','A','B','C','D','E'], ['a','b','c','d','e'], 'S', prods)
        
        final_glc = convert_terminals_and_binarize(glc)
        
        for p in final_glc.productions:
            self.assertTrue(len(p.rhs) <= 2, f"Regra longa demais sobrou: {p}")
            # Se for binária, deve apontar para variáveis
            if len(p.rhs) == 2:
                self.assertTrue(all(s.isupper() or '_' in s for s in p.rhs))

        new_vars = [v for v in final_glc.variables if "C_" in v or "X" in v] 
        self.assertTrue(len(new_vars) > 0, "Nenhuma variável auxiliar foi criada para binarização")

    def test_mixed_terminals_and_variables(self):
        """Testa isolamento de terminais no meio de variáveis: S -> a A b B"""
        prods = [
            self.create_prod('S', 'aAbB'),
            self.create_prod('A', 'x'),
            self.create_prod('B', 'y')
        ]
        glc = GLC(['S','A','B'], ['a','b','x','y'], 'S', prods)
        
        final_glc = convert_terminals_and_binarize(glc)
        res_set = self.prods_to_set(final_glc.productions)
        
        self.assertNotIn("S -> aAbB", res_set)
        
        terminal_rules = [p for p in final_glc.productions if len(p.rhs) == 1 and p.rhs[0] in ['a', 'b']]
        self.assertTrue(len(terminal_rules) >= 2, "Não isolou os terminais a e b")

    def test_unit_cycles(self):
        """Testa loops unitários: A -> B, B -> C, C -> A. Deve resolver sem loop infinito."""

        prods = [
            self.create_prod('S', 'A'), 
            self.create_prod('A', 'B'),
            self.create_prod('B', 'C'),
            self.create_prod('C', 'A'),
            self.create_prod('A', 'a') 
        ]
        glc = GLC(['S','A','B','C'], ['a'], 'S', prods)
        
        new_glc = remove_unit_productions(glc)
        res_set = self.prods_to_set(new_glc.productions)
        
        self.assertIn("S -> a", res_set)
        self.assertIn("B -> a", res_set)
        self.assertIn("C -> a", res_set)
        self.assertNotIn("A -> B", res_set)
        self.assertNotIn("B -> C", res_set)

    def test_full_pipeline_integration(self):
        """Simula o fluxo completo do main.py manualmente"""
               
        prods = [
            self.create_prod('S', 'ASA'),
            self.create_prod('S', 'aB'),
            Production('S', ['&']),
            self.create_prod('B', 'b'),
            Production('B', ['&']),
            self.create_prod('D', 'd')
        ]
        glc = GLC(['S', 'B', 'D'], ['a', 'b', 'd'], 'S', prods)

        step1_prods = remove_empty_productions(glc.productions)
        glc.productions = remove_duplicate_productions(step1_prods)
        
        glc = remove_unit_productions(glc)
        
        glc = remove_useless_symbols(glc)
        
        glc = convert_terminals_and_binarize(glc)
        
        final_vars = glc.variables
        final_prods = self.prods_to_set(glc.productions)
        
        self.assertNotIn('D', final_vars)
        
        for p in glc.productions:
            self.assertFalse(p.is_epsilon(), f"Sobrou epsilon: {p}")
            self.assertTrue(len(p.rhs) <= 2)
            if len(p.rhs) == 2:
                self.assertFalse(p.rhs[0] in glc.alphabet)
                self.assertFalse(p.rhs[1] in glc.alphabet)


if __name__ == '__main__':
    unittest.main()
