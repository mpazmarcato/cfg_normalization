import unittest
from models import GLC, Production

class TestModels(unittest.TestCase):

    def test_production_creation_and_repr(self):
        """Testa a representação em string e criação básica."""
        p1 = Production("S", ["A", "B"])
        self.assertEqual(str(p1), "S -> AB")
        
        p2 = Production("A", ["&"])
        self.assertEqual(str(p2), "A -> &")

    def test_is_epsilon(self):
        """Testa detecção de produção vazia."""
        p_empty = Production("A", ["&"])
        self.assertTrue(p_empty.is_epsilon())

        p_not_empty = Production("A", ["B"])
        self.assertFalse(p_not_empty.is_epsilon())

    def test_is_unit(self):
        """Testa detecção de produção unitária."""
        p_unit = Production("S", ["A"]) 
        self.assertTrue(p_unit.is_unit())

        p_term = Production("S", ["a"]) 
        self.assertFalse(p_term.is_unit())

        p_long = Production("S", ["A", "B"])
        self.assertFalse(p_long.is_unit())

    def test_glc_copy(self):
        """Testa se a cópia da GLC é profunda (deep copy) para produções."""
        p1 = Production("S", ["A"])
        glc = GLC(["S", "A"], ["a"], "S", [p1])
        
        glc_copy = glc.copy()
        
        glc_copy.productions[0].rhs = ["B"]
        
        self.assertEqual(glc.productions[0].rhs, ["A"])
        self.assertEqual(glc_copy.productions[0].rhs, ["B"])

if __name__ == '__main__':
    unittest.main()
