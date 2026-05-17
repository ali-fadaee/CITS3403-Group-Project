import multiprocessing
import time
from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

localHost = "http://127.0.0.1:5000/"

def create_test_data(db):
    from app.models import User, Debate, Tag, Comment, CommentSide
    user = User(username='seleniumuser', email='selenium@example.com', email_verified=True)
    user.set_password('Password1')
    db.session.add(user)
    db.session.flush()

    tag = Tag(name='science')
    db.session.add(tag)

    debate1 = Debate(title='Should AI replace developers?', creator_id=user.id)
    debate1.tags.append(tag)
    debate2 = Debate(title='Is Python better than JavaScript?', creator_id=user.id)
    db.session.add(debate1)
    db.session.add(debate2)
    db.session.flush()

    # seed an argument so the arguments tab has content
    comment = Comment(debate_id=debate1.id, user_id=user.id,
                      content='AI will never fully replace human creativity.',
                      side=CommentSide.no)
    db.session.add(comment)

    # seed a saved debate so the saved tab has content
    user.saved.append(debate2)

    db.session.commit()

def run_flask_app():
    from dotenv import load_dotenv
    load_dotenv()
    from app import create_app, db
    from app.config import TestConfig
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all() # ensure a clean slate for testing
        db.create_all()
        create_test_data(db)
    app.run(use_reloader=False, debug=False)

class SeleniumTests(TestCase):
    def setUp(self):
        self.server_thread = multiprocessing.Process(target=run_flask_app)
        self.server_thread.start()
        time.sleep(1.5)  # Wait for server to start
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1920, 1080)

    def tearDown(self):
        self.server_thread.terminate()
        self.server_thread.join() # ensure the process has fully stopped
        self.driver.quit()

# Selenium tests for authentication functionality, including login and signup
class AuthSeleniumTests(SeleniumTests):
    def test_login_success(self):
        # Verify that a valid username and password logs the user in and lands on an authenticated page
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        body = self.driver.page_source
        assert "logout" in body or "profile" in body

    def test_login_invalid_password(self):
        # Verify that an incorrect password shows an error message and does not log the user in
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("WrongPassword")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        try:
            error = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Invalid username/email or password')]"))
            )
        except Exception:
            error = None
        assert error is not None, "Expected error message not found for invalid login."

    def test_signup_success(self):
        # Verify that completing the two-step signup form redirects to an email verification prompt
        self.driver.get(localHost + "signup")
        self.driver.find_element(By.NAME, "email").send_keys("seleniumsignup@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("Password1")
        continue_btn = self.driver.find_element(By.ID, "continueToProfile")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn)
        self.driver.execute_script("arguments[0].click();", continue_btn)

        time.sleep(0.5)  # wait for CSS transition to complete
        self.driver.find_element(By.NAME, "username").send_keys("seleniumsignup")
        self.driver.find_element(By.NAME, "signupSubmit").click()
        body = self.driver.page_source
        assert "check your email" in body


# Selenium tests for the index/debate listing page
class IndexSeleniumTests(SeleniumTests):
    def _login(self):
        # Helper: log in as the seeded test user before running a test
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(localHost + "login"))

    def test_index_loads(self):
        # Verify that the index page renders with the debate listing and filter tabs visible
        self.driver.get(localHost)
        body = self.driver.page_source
        assert "debates" in body
        assert "for you" in body or "popular" in body

    def test_index_shows_debates(self):
        # Verify that seeded debates appear as cards on the index page
        self.driver.get(localHost + "?filter=popular")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debate-card"))
        )
        cards = self.driver.find_elements(By.CLASS_NAME, "debate-card")
        assert len(cards) >= 2

    def test_index_filter_tab_changes_active(self):
        # Verify that clicking a filter tab updates the active tab style and the URL filter parameter
        self.driver.get(localHost + "?filter=popular")
        new_tab = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'filter-tab') and text()='new']"))
        )
        new_tab.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'filter-tab') and contains(@class,'is-active') and text()='new']"))
        )
        assert "filter=new" in self.driver.current_url

    def test_index_debate_card_navigates_to_debate(self):
        # Verify that clicking a debate card navigates to that debate's detail page
        self.driver.get(localHost + "?filter=popular")
        card = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "debate-card"))
        )
        card.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("/debate/"))
        assert "/debate/" in self.driver.current_url

    def test_index_tag_filter_applied(self):
        # Verify that clicking a tag on a debate card filters the listing to that tag and updates the URL
        self.driver.get(localHost + "?filter=popular")
        tag = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "debate-tag"))
        )
        tag_name = tag.text
        tag.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("tag="))
        assert f"tag={tag_name}" in self.driver.current_url
        body = self.driver.page_source
        assert tag_name in body

    def test_index_per_page_selector(self):
        # Verify that clicking a per-page option updates the per_page URL parameter
        self.driver.get(localHost + "?filter=popular&per_page=10")
        btn_25 = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'per-page-btn') and text()='25']"))
        )
        btn_25.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("per_page=25"))
        assert "per_page=25" in self.driver.current_url

    def test_index_new_debate_btn_anonymous_redirects(self):
        # Verify that an anonymous user clicking "new --debate" is redirected away from the index
        self.driver.get(localHost)
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(localHost))
        assert "login" in self.driver.current_url or "create" in self.driver.current_url

    def test_index_new_debate_btn_authenticated_opens_modal(self):
        # Verify that a logged-in user clicking "new --debate" opens the create debate modal
        self._login()
        self.driver.get(localHost + "?filter=popular")
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        modal = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createModal"))
        )
        assert modal.is_displayed()

    def test_index_save_button_visible_when_authenticated(self):
        # Verify that save buttons appear on debate cards when the user is logged in
        self._login()
        self.driver.get(localHost + "?filter=popular")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card-save-btn"))
        )
        save_btns = self.driver.find_elements(By.CLASS_NAME, "card-save-btn")
        assert len(save_btns) > 0

    def test_index_save_button_not_visible_when_anonymous(self):
        # Verify that save buttons are not rendered on debate cards for anonymous users
        self.driver.get(localHost + "?filter=popular")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debate-card"))
        )
        save_btns = self.driver.find_elements(By.CLASS_NAME, "card-save-btn")
        assert len(save_btns) == 0


# Selenium tests for the my-activity page (debates, arguments, and saved tabs)
class MyActivitySeleniumTests(SeleniumTests):
    def _login(self):
        # Helper: log in as the seeded test user before running a test
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(localHost + "login"))

    def test_my_activity_requires_login(self):
        # Verify that anonymous users are redirected to login when accessing my-activity
        self.driver.get(localHost + "debates/mine")
        WebDriverWait(self.driver, 5).until(EC.url_contains("login"))
        assert "login" in self.driver.current_url

    def test_my_activity_loads(self):
        # Verify that the my-activity page renders with the three tab options visible
        self._login()
        self.driver.get(localHost + "debates/mine")
        body = self.driver.page_source
        assert "debates" in body
        assert "arguments" in body
        assert "saved" in body

    def test_my_activity_debates_tab_is_default(self):
        # Verify that the debates tab is active by default when no tab param is provided
        self._login()
        self.driver.get(localHost + "debates/mine")
        active_tab = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'filter-tab') and contains(@class,'is-active')]"))
        )
        assert active_tab.text == "debates"

    def test_my_activity_debates_tab_shows_user_debates(self):
        # Verify that the debates tab lists debates created by the logged-in user
        self._login()
        self.driver.get(localHost + "debates/mine?tab=debates")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debate-card"))
        )
        cards = self.driver.find_elements(By.CLASS_NAME, "debate-card")
        assert len(cards) >= 2

    def test_my_activity_arguments_tab_shows_user_arguments(self):
        # Verify that the arguments tab lists arguments (comments) posted by the logged-in user
        self._login()
        self.driver.get(localHost + "debates/mine?tab=arguments")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debate-card"))
        )
        cards = self.driver.find_elements(By.CLASS_NAME, "debate-card")
        assert len(cards) >= 1

    def test_my_activity_saved_tab_shows_saved_debates(self):
        # Verify that the saved tab lists debates the user has bookmarked
        self._login()
        self.driver.get(localHost + "debates/mine?tab=saved")
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debate-card"))
        )
        cards = self.driver.find_elements(By.CLASS_NAME, "debate-card")
        assert len(cards) >= 1

    def test_my_activity_tab_switch_updates_url(self):
        # Verify that clicking a tab updates the tab parameter in the URL
        self._login()
        self.driver.get(localHost + "debates/mine")
        args_tab = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'filter-tab') and text()='arguments']"))
        )
        args_tab.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("tab=arguments"))
        assert "tab=arguments" in self.driver.current_url

    def test_my_activity_debate_card_navigates_to_debate(self):
        # Verify that clicking a debate card on the debates tab navigates to that debate's page
        self._login()
        self.driver.get(localHost + "debates/mine?tab=debates")
        card = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "debate-card"))
        )
        card.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("/debate/"))
        assert "/debate/" in self.driver.current_url

    def test_my_activity_new_debate_btn_opens_modal(self):
        # Verify that clicking "new --debate" opens the create debate modal
        self._login()
        self.driver.get(localHost + "debates/mine")
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        modal = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createModal"))
        )
        assert modal.is_displayed()

    def test_my_activity_home_btn_navigates_to_index(self):
        # Verify that clicking "cd --home" navigates back to the index page
        self._login()
        self.driver.get(localHost + "debates/mine")
        home_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "my-debates-btn"))
        )
        home_btn.click()
        WebDriverWait(self.driver, 5).until(EC.url_to_be(localHost))
        assert self.driver.current_url == localHost

    def test_my_activity_per_page_selector(self):
        # Verify that clicking a per-page option updates the per_page URL parameter
        self._login()
        self.driver.get(localHost + "debates/mine?tab=debates&per_page=10")
        btn_25 = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'per-page-btn') and text()='25']"))
        )
        btn_25.click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("per_page=25"))
        assert "per_page=25" in self.driver.current_url

class CreateDebateSeleniumTests(SeleniumTests):
    def _login(self):
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(localHost + "login"))
    
    def test_create_debate_modal_opens(self):
        # Verify that clicking "new --debate" opens the create debate modal
        self._login()
        self.driver.get(localHost)
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        modal = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createModal"))
        )
        assert modal.is_displayed()

    def test_create_debate_category_chip_toggles(self):
        # Verify that clicking a category chip marks it as selected
        self._login()
        self.driver.get(localHost)
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createModal"))
        )
        chip = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#createCategoryGrid .category-chip"))
        )
        chip.click()
        assert "is-selected" in chip.get_attribute("class")

    def test_create_debate_empty_thesis_shows_error(self):
        # Verify that submitting without a thesis shows an inline error message
        self._login()
        self.driver.get(localHost)
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createModal"))
        )
        chip = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#createCategoryGrid .category-chip"))
        )
        chip.click()
        self.driver.find_element(By.ID, "createDebateBtn").click()
        error_el = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createError"))
        )
        assert "empty" in error_el.text.lower() or "cannot" in error_el.text.lower()
    
    def test_create_debate_submit_redirects_to_debate_page(self):
        # Verify that submitting a valid thesis and category redirects to /debate/<id>
        self._login()
        self.driver.get(localHost)
        btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "new-debate-btn"))
        )
        btn.click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "createModal"))
        )
        self.driver.find_element(By.ID, "thesisInput").send_keys(
            "Should automation replace manual jobs?"
        )
        chip = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#createCategoryGrid .category-chip"))
        )
        chip.click()
        self.driver.find_element(By.ID, "createDebateBtn").click()
        WebDriverWait(self.driver, 10).until(EC.url_contains("/debate/"))
        assert "/debate/" in self.driver.current_url


# Selenium tests for the profile modal
class ProfileSeleniumTests(SeleniumTests):
    def _login(self):
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(localHost + "login"))

    def _open_profile_modal(self):
        chip = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "profile-chip"))
        )
        chip.click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "profileFullModal"))
        )
    
    def test_profile_modal_opens(self):
        # Verify that clicking the profile chip opens the profile modal
        self._login()
        self.driver.get(localHost)
        self._open_profile_modal()
        modal = self.driver.find_element(By.ID, "profileFullModal")
        assert modal.is_displayed()

    def test_profile_password_toggle_shows_fields(self):
        # Verify that clicking "$ change" reveals the password input fields
        self._login()
        self.driver.get(localHost)
        self._open_profile_modal()
        change_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "changePwBtn"))
        )
        change_btn.click()
        pw_fields = self.driver.find_element(By.ID, "pwChangeFields")
        assert pw_fields.is_displayed()
    
    def test_profile_interests_modal_opens(self):
        # Verify that clicking "= add" opens the interests sub-modal
        self._login()
        self.driver.get(localHost)
        self._open_profile_modal()
        add_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "addInterestBtn"))
        )
        add_btn.click()
        interests_modal = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "interestsModal"))
        )
        assert interests_modal.is_displayed()
    
    def test_profile_avatar_modal_opens(self):
        # Verify that clicking the avatar button opens the avatar picker sub-modal
        self._login()
        self.driver.get(localHost)
        self._open_profile_modal()
        avatar_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "avatarBtn"))
        )
        avatar_btn.click()
        avatar_modal = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "avatarModal"))
        )
        assert avatar_modal.is_displayed()
    
    def test_profile_username_displayed_correctly(self):
        # Verify that the logged-in user's username appears in the profile modal
        self._login()
        self.driver.get(localHost)
        self._open_profile_modal()
        username_span = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='profileFullModal']//span[contains(@class,'field-static') and text()='seleniumuser']")
            )
        )
        assert username_span.text == "seleniumuser"
    
    def test_profile_weak_password_shows_error(self):
        # Verify that entering a new password that fails requirements shows an inline error
        self._login()
        self.driver.get(localHost)
        self._open_profile_modal()
        change_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "changePwBtn"))
        )
        change_btn.click()
        self.driver.find_element(By.ID, "currentPassword").send_keys("Password1")
        self.driver.find_element(By.ID, "newPassword").send_keys("weak")
        self.driver.find_element(By.ID, "confirmPassword").send_keys("weak")
        self.driver.find_element(By.ID, "saveProfileBtn").click()
        error = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "profileError"))
        )
        assert error.is_displayed()
        assert len(error.text) > 0


# Selenium tests for the debate tree page
class DebateTreeSeleniumTests(SeleniumTests):
    def _login(self):
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        WebDriverWait(self.driver, 5).until(EC.url_changes(localHost + "login"))

    def test_debate_page_loads_thread_with_topic_author(self):
        # Verify that the debate page loads the thread and shows the topic author
        self.driver.get(localHost + "debate/1")
        author = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.ID, "topic-author"))
        )
        comment = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'AI will never fully replace human creativity.')]")
            )
        )
        assert "@seleniumuser" in author.text
        assert comment is not None

    def test_debate_add_comment_shows_in_yes_column(self):
        # Verify that adding a yes comment displays it on the debate page
        self._login()
        self.driver.get(localHost + "debate/1")
        add_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "add-comment-yes"))
        )
        add_btn.click()
        comment_text = "Selenium yes argument"
        self.driver.find_element(By.ID, "comment-input").send_keys(comment_text)
        self.driver.find_element(By.CSS_SELECTOR, "#comment-form .send-button").click()
        added_comment = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[@id='yes-options']//*[contains(text(), '{comment_text}')]")
            )
        )
        assert added_comment is not None
