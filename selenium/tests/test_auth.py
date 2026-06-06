from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers.auth import DEFAULT_PASSWORD, login_user, register_user, unique_username
from helpers.clicks import safe_click


def test_register_and_reach_home(driver, wait, base_url):
    register_user(driver, wait, base_url)
    assert driver.find_element(By.XPATH, "//h1[contains(text(), 'Welcome!')]")
    assert driver.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")


def test_login_with_existing_user(driver, wait, base_url):
    username = unique_username()
    register_user(driver, wait, base_url, username)
    safe_click(driver, driver.find_element(By.XPATH, "//button[contains(text(), 'Logout')]"))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Login')]")))

    login_user(driver, wait, base_url, username, DEFAULT_PASSWORD)
    assert driver.find_element(By.XPATH, "//h1[contains(text(), 'Welcome!')]")


def test_logout_redirects_to_login(driver, wait, base_url):
    register_user(driver, wait, base_url)
    safe_click(driver, driver.find_element(By.XPATH, "//button[contains(text(), 'Logout')]"))
    wait.until(lambda d: d.current_url.rstrip("/").endswith("/login"))
    assert driver.find_element(By.XPATH, "//h2[contains(text(), 'Login')]")
