from selenium.webdriver import Chrome, ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def create_chromedriver():
    chrome_driver_path = ChromeDriverManager().install()
    service = ChromeService(chrome_driver_path=chrome_driver_path)
    return Chrome(service=service)
