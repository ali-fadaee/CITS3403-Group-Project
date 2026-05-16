import multiprocessing
import time
from unittest import TestCase
from selenium import webdriver

localHost = "http://127.0.0.1:5000/"

def run_flask_app():
    from dotenv import load_dotenv
    load_dotenv()
    from app import create_app, db
    from app.config import TestConfig
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    app.run(use_reloader=False, debug=False)

class SeleniumTests(TestCase):
    def setUp(self):
        self.server_thread = multiprocessing.Process(target=run_flask_app)
        self.server_thread.start()
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.quit()
    
    # Add your Selenium tests here
    def test_example(self):
        self.driver.get(localHost)
        time.sleep(1)