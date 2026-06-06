import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="function")
def base_url():
    return os.getenv("BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    if remote_url:
        browser = webdriver.Remote(command_executor=remote_url, options=options)
    else:
        browser = webdriver.Chrome(options=options)

    yield browser
    browser.quit()


@pytest.fixture(scope="function")
def wait(driver):
    return WebDriverWait(driver, 10)
