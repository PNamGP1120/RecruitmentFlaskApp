# tests/test_example.py
import unittest
from app.models import User
from app import app, dao

class SimpleTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)

