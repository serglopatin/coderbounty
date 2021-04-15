from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotVisibleException,
)
from selenium.webdriver import Remote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from contextlib import contextmanager
from django.test import LiveServerTestCase
import os
from django.conf import settings
import time

os.environ["DJANGO_LIVE_TEST_SERVER_ADDRESS"] = "localhost:8082"

from django.test.utils import override_settings
from selenium.webdriver.firefox.webdriver import WebDriver


class MySeleniumTests(LiveServerTestCase):
    fixtures = ["initial_data.json"]

    def wait_for_visibility(self, selector, timeout_seconds=20):
        retries = timeout_seconds
        while retries:
            try:
                element = self.selenium.find_element_by_class_name(selector)
                if element.is_displayed():
                    return element
            except (NoSuchElementException, StaleElementReferenceException):
                if retries <= 0:
                    raise
                else:
                    pass

            retries = retries - 1
            time.sleep(1)
        raise ElementNotVisibleException(
            "Element %s not visible despite waiting for %s seconds"
            % (selector, timeout_seconds)
        )

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    @override_settings(DEBUG=True)
    def test_signup(self):
        self.selenium.get("%s%s" % (self.live_server_url, "/accounts/signup/"))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("myuser2")
        username_input = self.selenium.find_element_by_name("email")
        username_input.send_keys("myuser@myuser.com")
        password_input = self.selenium.find_element_by_name("password1")
        password_input.send_keys("secret")
        password_input = self.selenium.find_element_by_name("password2")
        password_input.send_keys("secret")
        self.selenium.find_element_by_id("sign_up").click()

        self.wait_for_visibility("success")
        assert "myuser" in self.selenium.title.lower()

    # @override_settings(DEBUG=True)
    # def test_post_bounty(self):
    #     self.selenium.get("%s%s" % (self.live_server_url, "/accounts/login/"))
    #     username_input = self.selenium.find_element_by_name("login")
    #     username_input.send_keys("myuser")
    #     password_input = self.selenium.find_element_by_name("password")
    #     password_input.send_keys("secret")
    #     self.selenium.find_element_by_id("log_in").click()

    #     # self.selenium.find_element_by_xpath(
    #     #     "/html/body/div/div[1]/div/section/div/div/form/div/button"
    #     # ).click()
    #     self.wait_for_visibility("success")
    #     response = self.selenium.get("%s%s" % (self.live_server_url, "/post/"))
    #     username_input = self.selenium.find_element_by_name("issueUrl")
    #     username_input.send_keys("https://github.com/twbs/bootstrap/issues/21814")
    #     username_input = self.selenium.find_element_by_name("title")
    #     username_input.send_keys("test")
    #     username_input = self.selenium.find_element_by_name("content")
    #     username_input.send_keys("test")
    #     self.selenium.find_element_by_xpath(
    #         '//*[@id="post_bounty"]/div[2]/div[3]/button'
    #     ).click()

    #     self.wait_for_visibility("ng-binding")
    #     self.selenium.switch_to_frame("injectedUl")
    #     self.wait_for_visibility("hasHelp")
    #     email_input = self.selenium.find_element_by_id("email")
    #     email_input.send_keys(settings.PAYPAL_SANDBOX_EMAIL)
    #     password_input = self.selenium.find_element_by_id("password")
    #     password_input.send_keys(settings.PAYPAL_SANDBOX_PASSWORD)
    #     self.selenium.find_element_by_name("btnLogin").click()

    #     time.sleep(10)
    #     self.selenium.switch_to_default_content()
    #     time.sleep(1)
    #     self.wait_for_visibility("reviewSections")
    #     self.selenium.find_element_by_id("confirmButtonTop").click()

    #     time.sleep(10)
    #     self.selenium.switch_to_default_content()
    #     time.sleep(1)
    #     self.wait_for_visibility("view-ghithub")
    #     assert "$20" in self.selenium.find_element_by_class_name("total").text
