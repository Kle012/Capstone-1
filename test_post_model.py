""" Post model tests."""

# FLASK_ENV=production python -m unittest test_post_model.py

import os
from unittest import TestCase

from models import db, User, Post

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

app.app_context().push()

db.create_all()

class PostModelTestCase(TestCase):
    """Test view for posts."""
    
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 98765
        u = User.signup('testp', 'tpost', 'post_test', 'messages@test.com', 'password', None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        """Does the basic model work?"""
        
        m = Post(
            text='Hello',
            user_id = self.uid
        )

        db.session.add(m)
        db.session.commit()

        #User should have 1 post

        self.assertEqual(len(self.u.posts), 1)
        self.assertEqual(self.u.posts[0].text, 'Hello')