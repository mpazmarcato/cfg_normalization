import unittest
import os
from parser import parse_set, parse_production, create_grammar

class TestParser(unittest.TestCase):

    def test_parse_set(self):
        """Testa conversão de string '{A, B}' para lista."""
        self.assertEqual(parse_set("{A, B, C}"), ["A", "B", "C"])
        self.assertEqual(parse_set(" { A ,  B } "), ["A", "B"])
        self.assertEqual(parse_set("S"), ["S"])

    def test_parse_production_simple(self):
        """Testa leitura de regras simples."""
        res = parse_production("S -> A B")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].lhs, "S")
        self.assertEqual(res[0].rhs, ["A", "B"])

    def test_parse_production_pipe(self):
        """Testa leitura de regras com OU logic (|)."""
        res = parse_production("S -> A | B")
        self.assertEqual(len(res), 2)
        prods = {str(p) for p in res}
        self.assertIn("S -> A", prods)
        self.assertIn("S -> B", prods)

    def test_parse_production_epsilon(self):
        """Testa leitura de epsilon/lambda."""
        res = parse_production("A -> &")
        self.assertTrue(res[0].is_epsilon())
        
        res2 = parse_production("A -> ε")
        self.assertTrue(res2[0].is_epsilon())

    def test_create_grammar_from_file(self):
        """Cria um arquivo temporário e testa o carregamento completo."""
        filename = "temp_test_grammar.txt"
        content = """
        Variaveis = {S, A}
        Alfabeto = {a, b}
        Inicial = S
        Regras:
        S -> A S | a
        A -> b
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        try:
            glc = create_grammar(filename)
            self.assertEqual(glc.start, "S")
            self.assertEqual(set(glc.variables), {"S", "A"})
            self.assertEqual(set(glc.alphabet), {"a", "b"})
            self.assertEqual(len(glc.productions), 3)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()