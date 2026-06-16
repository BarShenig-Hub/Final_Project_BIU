import unittest
from app import make_couple_id

class TestApp(unittest.TestCase):
    def test_make_couple_id(self):
        result = make_couple_id("john", "doe")
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()