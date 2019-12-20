import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def password_test_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.hashed_password is not None)

    def password_test_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.check_password('cat'))

    def test_password_are_random(self):
        u = User(password='cat')
        su = User(password='cat')

        self.assertTrue(u.hashed_password != su.hashed_password)