def safe_click(driver, element):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", element
    )
    driver.execute_script("arguments[0].click();", element)
