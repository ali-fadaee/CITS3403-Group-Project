from unittest import TestCase

from app import create_app, db
from app.config import TestConfig

class BasicTests(TestCase):
    def setUp(self):
        testApp =  create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    # Add your unit tests here
    def test_example(self):
        self.assertTrue(True)