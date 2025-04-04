import math
import random
from selenium.webdriver.common.action_chains import ActionChains
import time
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


def create_chromedriver():
    chrome_driver_path = ChromeDriverManager().install()
    return uc.Chrome(
        driver_executable_path=chrome_driver_path,
        # browser_executable_path=browser_path,
        use_subprocess=True,
    )


def type_like_human(element, text, mean_delay=0.1, sigma=0.5):
    for char in text:
        element.send_keys(char)
        delay = max(random.lognormvariate(math.log(mean_delay), sigma), 0)
        time.sleep(delay)


def move_and_click(driver, element, force_click=False):
    actions = ActionChains(driver)
    chain = actions.move_to_element(element)
    if force_click:
        chain.perform()
        element.click()
    else:
        chain.click().perform()
