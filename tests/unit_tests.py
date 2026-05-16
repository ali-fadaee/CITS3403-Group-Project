from unittest import TestCase

from app import create_app, db
from app.config import TestConfig

def create_test_data():
    from app.models import User
    # create a verified test user for testing login functionality
    user1 = User(username='user1', email='test@example.com', email_verified=True)
    user1.set_password('Password1')
    # create an unverified test user for testing email verification functionality
    user2 = User(username='user2', email='unverified@example.com', email_verified=False)
    user2.set_password('Password1')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

class BasicTests(TestCase):
    def setUp(self):
        testApp =  create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        create_test_data()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
    
class AuthTests(BasicTests):
    # Unit tests for authentication functionality, including login and signup 
    # Tests for login with invalid password
    def test_login_invalid_password(self):
        client = self.app_context.app.test_client()
        response = client.post('/login', data={
            'usernameEmail': 'user1',
            'password': 'WrongPassword',
            'loginSubmit': True
        }, follow_redirects=True)
        self.assertIn(
            b'Invalid username/email or password',
            response.data,
            "Login with wrong password did not show error."
        )

    # Tests for login with unverified email
    def test_login_unverified_email(self):
        client = self.app_context.app.test_client()
        response = client.post('/login', data={
            'usernameEmail': 'user2',
            'password': 'Password1',
            'loginSubmit': True
        }, follow_redirects=True)
        self.assertIn(
            b'Please verify your email before logging in.',
            response.data,
            "Login with unverified email did not show error."
        )
    
    # Tests for successful login
    def test_login_success(self):
        client = self.app_context.app.test_client()
        response = client.post('/login', data={
            'usernameEmail': 'user1',
            'password': 'Password1',
            'loginSubmit': True
        }, follow_redirects=True)
        self.assertTrue(
            b'logout' in response.data or b'profile' in response.data,
            "Login did not succeed as expected."
        )
    
    # Tests check for successful signup
    def test_signup_success(self):
        client = self.app_context.app.test_client()
        response = client.post('/signup', data={
            'email': 'test1@example.com',
            'username': 'testuser1',
            'password': 'Password1',
            'confirm_password': 'Password1',
            'signupSubmit': True
        }, follow_redirects=True)
        self.assertIn(
            b'check your email',
            response.data,
            "Signup did not prompt to check email."
        )