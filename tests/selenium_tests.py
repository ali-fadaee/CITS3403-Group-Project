import multiprocessing
import time
from unittest import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

localHost = "http://127.0.0.1:5000/"

def create_test_data(db):
    from app.models import User
    user = User(username='seleniumuser', email='selenium@example.com', email_verified=True)
    user.set_password('Password1')
    db.session.add(user)
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

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.quit()

# Selenium tests for authentication functionality, including login and signup   
class AuthSeleniumTests(SeleniumTests):
    def test_login_success(self):
        self.driver.get(localHost + "login")
        self.driver.find_element(By.NAME, "usernameEmail").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "password").send_keys("Password1")
        self.driver.find_element(By.NAME, "loginSubmit").click()
        body = self.driver.page_source
        assert "logout" in body or "profile" in body

    def test_login_invalid_password(self):
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