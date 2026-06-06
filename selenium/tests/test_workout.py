import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from helpers.auth import register_user
from helpers.clicks import safe_click
from helpers.select import select_react_option


@pytest.fixture(autouse=True)
def authenticated_user(driver, wait, base_url):
    register_user(driver, wait, base_url)


def _create_workout(driver, wait, workout_name, description):
    driver.find_element(By.ID, "workoutName").send_keys(workout_name)
    driver.find_element(By.ID, "workoutDescription").send_keys(description)
    collapse_one = driver.find_element(By.ID, "collapseOne")
    safe_click(driver, collapse_one.find_element(By.CSS_SELECTOR, "form button[type='submit']"))
    wait.until(lambda d: d.find_element(By.ID, "workoutName").get_attribute("value") == "")


def _open_routine_section(driver, wait):
    safe_click(driver, driver.find_element(By.CSS_SELECTOR, '[data-bs-target="#collapseTwo"]'))
    wait.until(EC.visibility_of_element_located((By.ID, "routineName")))


def _select_workout(driver, wait, workout_name):
    wait.until(
        lambda d: workout_name
        in [opt.text for opt in Select(d.find_element(By.ID, "workoutSelect")).options]
    )
    select_react_option(driver, "workoutSelect", workout_name)


def test_create_workout_visible_in_selector(driver, wait, base_url):
    workout_name = f"Workout {int(time.time() * 1000)}"

    _create_workout(driver, wait, workout_name, "E2E test workout")
    _open_routine_section(driver, wait)

    wait.until(
        lambda d: workout_name
        in [opt.text for opt in Select(d.find_element(By.ID, "workoutSelect")).options]
    )
    option_labels = [opt.text for opt in Select(driver.find_element(By.ID, "workoutSelect")).options]
    assert workout_name in option_labels


def test_create_routine_with_workout(driver, wait, base_url):
    workout_name = f"Workout {int(time.time() * 1000)}"
    routine_name = f"Routine {int(time.time() * 1000)}"

    _create_workout(driver, wait, workout_name, "Morning cardio")
    _open_routine_section(driver, wait)

    driver.find_element(By.ID, "routineName").send_keys(routine_name)
    driver.find_element(By.ID, "routineDescription").send_keys("Weekly plan")
    _select_workout(driver, wait, workout_name)
    safe_click(
        driver,
        driver.find_element(By.CSS_SELECTOR, "#collapseTwo form button[type='submit']"),
    )

    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//*[contains(., '{routine_name}')]")
        )
    )
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(., 'Morning cardio')]")
        )
    )
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, f"//li[contains(., '{workout_name}: Morning cardio')]")
        )
    )
