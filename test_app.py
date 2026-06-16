import unittest
import re
from app import make_couple_id

class TestAppFunctions(unittest.TestCase):

    def test_make_couple_id_formatting(self):
        """Test if names are converted to lowercase and spaces are replaced with dashes"""
        groom = " John "
        bride = "Doe "
        
        result = make_couple_id(groom, bride)
        
        # Why: We want to ensure user-input spaces are handled cleanly
        self.assertTrue(result.startswith("john-doe-"))

    def test_make_couple_id_special_characters(self):
        """Test if special non-alphanumeric characters are stripped, keeping English/Hebrew"""
        groom = "David!"
        bride = "רחל" # Testing your Hebrew character regex range (\u0590-\u05FF)
        
        result = make_couple_id(groom, bride)
        
        # Why: To make sure punctuation like '!' doesn't break URLs, but Hebrew strings persist
        self.assertIn("david-רחל", result)

    def test_make_couple_id_has_suffix(self):
        """Test that a short unique identifier suffix is appended"""
        result = make_couple_id("A", "B")
        
        # Why: The function truncates a uuid4 to 6 characters. Total segments: A + B + 6 characters = 3 parts
        parts = result.split("-")
        self.assertEqual(len(parts[-1]), 6)

if __name__ == "__main__":
    unittest.main()