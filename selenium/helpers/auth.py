import time
import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers.clicks import safe_click

DEFAULT_PASSWORD = "testpass123"


def unique_username() -> str:
    return f"selenium_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"


def register_user(driver, wait, base_url, username=None, password=DEFAULT_PASSWORD):
    username = username or unique_username()
    driver.get(f"{base_url}/login")
    driver.find_element(By.ID, "registerUsername").send_keys(username)
    driver.find_element(By.ID, "registerPassword").send_keys(password)
    register_form = driver.find_element(By.ID, "registerUsername").find_element(
        By.XPATH, "./ancestor::form"
    )
    submit_button = register_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    safe_click(driver, submit_button)
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h1[contains(text(), 'Welcome!')]")
        )
    )
    return {"username": username, "password": password}


def login_user(driver, wait, base_url, username, password=DEFAULT_PASSWORD):
    driver.get(f"{base_url}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    login_form = driver.find_element(By.ID, "username").find_element(
        By.XPATH, "./ancestor::form"
    )
    submit_button = login_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    safe_click(driver, submit_button)
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//h1[contains(text(), 'Welcome!')]")
        )
    )
