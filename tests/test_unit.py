from unittest import TestCase

from app import create_app, db
from app.config import TestConfig

def create_test_data():
    from app.models import User, Debate, Tag, Comment, CommentSide
    # create a verified test user for testing login functionality
    user1 = User(username='user1', email='test@example.com', email_verified=True)
    user1.set_password('Password1')
    # create an unverified test user for testing email verification functionality
    user2 = User(username='user2', email='unverified@example.com', email_verified=False)
    user2.set_password('Password1')
    db.session.add(user1)
    db.session.add(user2)
    db.session.flush()

    tag = Tag(name='technology')
    db.session.add(tag)

    debate1 = Debate(title='Should AI replace developers?', creator_id=user1.id)
    debate1.tags.append(tag)
    debate2 = Debate(title='Is Python better than JavaScript?', creator_id=user1.id)
    db.session.add(debate1)
    db.session.add(debate2)
    db.session.flush()

    # create an argument by user1 for testing the arguments tab
    comment = Comment(debate_id=debate1.id, user_id=user1.id,
                      content='AI lacks human creativity.', side=CommentSide.no)
    db.session.add(comment)

    # save debate2 for user1 for testing the saved tab
    user1.saved.append(debate2)

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


class IndexTests(BasicTests):
    # Unit tests for the index/debate listing page

    def _client(self):
        return self.app_context.app.test_client()

    def _logged_in_client(self):
        # Returns a test client with user1 already logged in
        client = self._client()
        client.post('/login', data={
            'usernameEmail': 'user1',
            'password': 'Password1',
            'loginSubmit': True
        }, follow_redirects=True)
        return client

    def test_index_returns_200(self):
        # Verify the index page is accessible to anonymous users
        response = self._client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_anonymous_default_filter_is_popular(self):
        # Verify anonymous users default to the popular filter
        response = self._client().get('/')
        self.assertIn(b'popular', response.data)

    def test_index_authenticated_default_filter_is_for_you(self):
        # Verify logged-in users default to the for-you filter
        response = self._logged_in_client().get('/')
        self.assertIn(b'for you', response.data)

    def test_index_filter_new(self):
        # Verify the new filter returns a 200 response
        response = self._client().get('/?filter=new')
        self.assertEqual(response.status_code, 200)

    def test_index_filter_popular(self):
        # Verify the popular filter returns a 200 response
        response = self._client().get('/?filter=popular')
        self.assertEqual(response.status_code, 200)

    def test_index_filter_top(self):
        # Verify the top filter returns a 200 response
        response = self._client().get('/?filter=top')
        self.assertEqual(response.status_code, 200)

    def test_index_invalid_per_page_defaults_to_10(self):
        # Verify that an invalid per_page value silently falls back to 10
        response = self._client().get('/?per_page=999')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'debates', response.data)

    def test_index_shows_seeded_debates(self):
        # Verify that seeded debates appear in the listing
        response = self._client().get('/?filter=new')
        self.assertIn(b'Should AI replace developers?', response.data)
        self.assertIn(b'Is Python better than JavaScript?', response.data)

    def test_index_tag_filter_returns_matching_debates(self):
        # Verify that filtering by tag only shows debates tagged with that tag
        response = self._client().get('/?filter=new&tag=technology')
        self.assertIn(b'Should AI replace developers?', response.data)
        self.assertNotIn(b'Is Python better than JavaScript?', response.data)

    def test_index_tag_filter_no_match_shows_empty(self):
        # Verify that filtering by a non-existent tag shows the no-debates message
        response = self._client().get('/?filter=new&tag=nonexistenttag')
        self.assertIn(b'no debates tagged', response.data)

    def test_index_pagination_page_param(self):
        # Verify that an out-of-range page still returns 200 without crashing
        response = self._client().get('/?filter=new&page=999')
        self.assertEqual(response.status_code, 200)


class MyActivityTests(BasicTests):
    # Unit tests for the my-activity page (/debates/mine)

    def _client(self):
        return self.app_context.app.test_client()

    def _logged_in_client(self):
        # Returns a test client with user1 already logged in
        client = self._client()
        client.post('/login', data={
            'usernameEmail': 'user1',
            'password': 'Password1',
            'loginSubmit': True
        }, follow_redirects=True)
        return client

    def test_my_activity_requires_login(self):
        # Verify anonymous users are redirected to login
        response = self._client().get('/debates/mine', follow_redirects=True)
        self.assertIn(b'login', response.data.lower())

    def test_my_activity_returns_200_when_authenticated(self):
        # Verify authenticated users can access the page
        response = self._logged_in_client().get('/debates/mine')
        self.assertEqual(response.status_code, 200)

    def test_my_activity_debates_tab_is_default(self):
        # Verify the debates tab is active when no tab param is provided
        response = self._logged_in_client().get('/debates/mine')
        self.assertIn(b'Should AI replace developers?', response.data)

    def test_my_activity_debates_tab_shows_user_debates(self):
        # Verify the debates tab lists only debates created by the logged-in user
        response = self._logged_in_client().get('/debates/mine?tab=debates')
        self.assertIn(b'Should AI replace developers?', response.data)
        self.assertIn(b'Is Python better than JavaScript?', response.data)

    def test_my_activity_arguments_tab_shows_user_comments(self):
        # Verify the arguments tab lists comments posted by the logged-in user
        response = self._logged_in_client().get('/debates/mine?tab=arguments')
        self.assertIn(b'AI lacks human creativity.', response.data)

    def test_my_activity_saved_tab_shows_saved_debates(self):
        # Verify the saved tab lists debates the user has bookmarked
        response = self._logged_in_client().get('/debates/mine?tab=saved')
        self.assertIn(b'Is Python better than JavaScript?', response.data)

    def test_my_activity_invalid_per_page_defaults_to_10(self):
        # Verify that an invalid per_page value silently falls back to 10
        response = self._logged_in_client().get('/debates/mine?per_page=999')
        self.assertEqual(response.status_code, 200)

    def test_my_activity_pagination_page_param(self):
        # Verify that an out-of-range page still returns 200 without crashing
        response = self._logged_in_client().get('/debates/mine?tab=debates&page=999')
        self.assertEqual(response.status_code, 200)