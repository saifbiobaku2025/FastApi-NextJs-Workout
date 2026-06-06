from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def select_react_option(driver, select_id, option_text):
    """Select an option in a React-controlled <select> and fire onChange."""
    select = Select(driver.find_element(By.ID, select_id))
    select.select_by_visible_text(option_text)
    driver.execute_script(
        """
        document.getElementById(arguments[0]).dispatchEvent(
            new Event('change', { bubbles: true })
        );
        """,
        select_id,
    )
