# tests/test_example.py
import unittest

class SimpleTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
