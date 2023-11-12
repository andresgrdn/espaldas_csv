import unittest
from main import MyLayout


class PruebaMyLayout(unittest.TestCase):
    def test_nombre_y_numero(self):
        myLayout = MyLayout()
        result = myLayout.parse_text('Andres 12')
        self.assertEqual(result, ('ANDRES', 12))

    def test_nombre_sin_numero(self):
        myLayout = MyLayout()
        result = myLayout.parse_text('Andres')
        self.assertEqual(result, ('ANDRES', 'BORRAR'))

    def test_numero_sin_nombre(self):
        myLayout = MyLayout()
        result = myLayout.parse_text('12')
        self.assertEqual(result, ('BORRAR', 12))

    def test_sin_nombre_y_numero(self):
        myLayout = MyLayout()
        result = myLayout.parse_text('')
        self.assertEqual(result, ('BORRAR', 'BORRAR'))

    def test_nombre_compuesto_y_numero(self):
        myLayout = MyLayout()
        result = myLayout.parse_text('Andres g. 12')
        self.assertEqual(result, ('ANDRES G.', 12))

    def test_nombre_compuesto_con_numero_y_numero(self):
        myLayout = MyLayout()
        result = myLayout.parse_text('Andres12 G. 12')
        self.assertEqual(result, ('ANDRES12 G.', 12))


if __name__ == '__main__':
    unittest.main()
