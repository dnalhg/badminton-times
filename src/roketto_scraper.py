from bs4 import BeautifulSoup
from common import ScrapingResult
from datetime import date, datetime, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import traceback
from util import create_chromedriver


class RokettoScraper:
    _driver: Chrome

    def __init__(self):
        self._driver = create_chromedriver()

    def scrape(self, day: date) -> ScrapingResult | None:
        pass


if __name__ == "__main__":
    scraper = RokettoScraper()
    try:
        day = datetime.strptime("2025-04-05", "%Y-%m-%d").date()
        for i in range(1):
            print(scraper.scrape(day + timedelta(days=i)))
    except Exception as e:
        print(e)
        traceback.print_exc()

    time.sleep(100000)
