# tests/test_example.py
import unittest
from app.models import User
from app import app, dao

class TestAuth(unittest.TestCase):
    def test_login(self):

