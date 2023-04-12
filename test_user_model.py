"""User model tests."""

# FLASK_ENV=production python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User
os.environ['DATABASE_URL'] = "postgresql:///weebs-test"

from app import app

app.app_context().push()

db.create_all()

class UserModelTestCase(TestCase):
    """Test view for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup('1test', 'u1', 'test1', 'test1@yahoo.com', 'password', None)
        u1d = 11111
        u1.id = u1d

        u2 = User.signup('2test', 'u2', 'test2', 'test2@yahoo.com', 'password', None)
        u2d = 22222
        u2.id = u2d

        db.session.commit()

        u1 = User.query.get(u1d)
        u2 = User.query.get(u2d)

        self.u1 = u1
        self.u1d = u1d
        
        self.u2 = u2
        self.u2d = u2d

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            first_name="test",
            last_name="t0",
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        #User should have no posts & no favorites

        self.assertEqual(len(u.posts), 0)
        self.assertEqual(len(u.favorites), 0)
    

    # User signup tests

    def test_valid_signup(self):
        """
        Does User.signup work with valid inputs?
        """

        u_test = User.signup('1test', 't1', 'testvalid', 'valid@test.com', 'password', None)
        uid = 99999
        u_test.id = uid

        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, 'testvalid')
        self.assertEqual(u_test.email, 'valid@test.com')
        self.assertNotEqual(u_test.password, 'password')

        # bcrypt strings start with $2b$

        self.assertTrue(u_test.password.startswith("$2b$"))
    
    def test_not_valid_email(self):
        """
        Does User.signup fail with invalid email?
        """

        not_valid = User.signup('email-test', 'tmail', 'not_valid', None, 'password', None)
        notid = 12345
        not_valid.id = notid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_not_valid_password(self):
        """
        Does User.signup fail with invalid password?
        """

        with self.assertRaises(ValueError) as context:
            User.signup('pass-test', 'tpass', "invalid_pass", "invalid@invalid.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup('pass-test', 'tpass',"invalid_pass", "invalid@invalid.com", None, None)
    

    # User authenticate tests
    
    def test_authenticate(self):
        """
        Does User.authenticate work with valid inputs?
        """

        u = User.authenticate(self.u1.username, 'password')
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1d)
    
    def test_invalid_username(self):
        """
        Does User.authenticate fail with invalid username?
        """

        self.assertFalse(User.authenticate('invalid_username', 'password'))
    
    def test_invalid_password(self):
        """
        Does User.authenticate fail with invalid password?
        """
        
        self.assertFalse(User.authenticate(self.u1.username, 'invalidpassword'))