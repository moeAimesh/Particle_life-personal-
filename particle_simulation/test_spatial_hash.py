import unittest
from main_classes import SpatialHashGrid, Particle

"""ONLY FOR INITIAL FUNCTIONALITY TESTINTG, TO BE DELETED LATER"""

class TestSpatialHashGrid(unittest.TestCase):
    def setUp(self):
        self.grid = SpatialHashGrid(cell_size=10)
        self.particle1 = Particle((5, 5))
        self.particle2 = Particle((15, 15))
        self.particle3 = Particle((100, 100))

        self.grid.insert(self.particle1)
        self.grid.insert(self.particle2)
        self.grid.insert(self.particle3)

    def test_insert(self):
        """Testet, ob Partikel korrekt in die Hashmap eingefügt werden."""
        self.assertEqual(len(self.grid.grid), 3)  # 3 verschiedene Zellen
        self.assertIn((0, 0), self.grid.grid)
        self.assertIn((1, 1), self.grid.grid)
        self.assertIn((10, 10), self.grid.grid)

    def test_query(self):
        """Testet die Nachbarsuche im gegebenen Radius."""
        result = self.grid.query((5, 5), radius=15)
        self.assertIn(self.particle1, result)
        self.assertIn(self.particle2, result)
        self.assertNotIn(self.particle3, result)  # Außerhalb des Radius
    

if __name__ == '__main__':
    unittest.main()
