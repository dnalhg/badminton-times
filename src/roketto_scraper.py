from bs4 import BeautifulSoup
from common import ScrapingResult
from datetime import date, datetime, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import traceback
from util import create_chromedriver, type_like_human


class RokettoScraper:

    _LOGIN_URL = "https://roketto.sportlogic.net.au/secure/customer/login"
    _BOOKING_URL = "https://roketto.sportlogic.net.au/secure/customer/booking/v1/public/show?readOnly=false&popupMsgDisabled=false&hideTopSiteBar=false"

    _driver: Chrome
    _username: str
    _password: str

    def __init__(self, username="", password=""):
        self._driver = create_chromedriver()

        self._username = username
        self._password = password

    def scrape(self, day: date) -> ScrapingResult | None:
        if day < datetime.now().date():
            print(f"{day} is before today")
            return None

        page_source = self._get_page_source(day)
        if page_source is None:
            return None

        soup = BeautifulSoup(page_source, "html.parser")
        table = soup.find("table", {"id": "calendar_view_table"})
        cells = table.find_all("td", {"class": "available"})

        available_start_times = set()
        for c in cells:
            info = c["onclick"]
            hour = int(info.split(",")[2].strip().strip("'").split(":")[0])
            available_start_times.add(hour)

        available_start_times = sorted(available_start_times)
        return ScrapingResult(
            location="roketto",
            branch="",
            day=day,
            available_times=[(i, i + 1) for i in available_start_times],
        )

    def _get_page_source(self, day: date):
        wait = WebDriverWait(self._driver, 2)

        if self._driver.current_url != self._BOOKING_URL:
            self._driver.get(self._BOOKING_URL)
        self._login()

        curr_booking_date = self._get_curr_booking_date()
        while curr_booking_date != day:
            if curr_booking_date < day:
                # Press next
                next = wait.until(
                    expected_conditions.visibility_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Next')]")
                    )
                )
                next.click()
                # move_and_click(self._driver, next)
            else:
                # Press prev
                prev = wait.until(
                    expected_conditions.visibility_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Previous')]")
                    )
                )
                prev.click()
                # move_and_click(self._driver, prev)
            time.sleep(1)
            new_booking_date = self._get_curr_booking_date()
            start = time.time()
            while new_booking_date == curr_booking_date:
                time.sleep(1)
                new_booking_date = self._get_curr_booking_date()
                if time.time() - start > 5:
                    return None

            curr_booking_date = new_booking_date

        wait.until(
            expected_conditions.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'table[id="calendar_view_table"]',
                )
            )
        )
        return self._driver.page_source

    def _login(self):
        curr_url = self._driver.current_url
        if curr_url != self._LOGIN_URL:
            return

        wait = WebDriverWait(self._driver, 2)
        username = wait.until(
            expected_conditions.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[id='userName']",
                )
            )
        )
        type_like_human(username, self._username)
        time.sleep(1)
        username.send_keys(Keys.TAB)
        time.sleep(1)

        password = wait.until(
            expected_conditions.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[id='userPassword']",
                )
            )
        )
        type_like_human(password, self._password)
        time.sleep(1)
        password.send_keys(Keys.RETURN)
        self._driver.get(self._BOOKING_URL)

    def _get_curr_booking_date(self):
        wait = WebDriverWait(self._driver, 2)
        date_span = wait.until(
            expected_conditions.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "span[id='date_heading']",
                )
            )
        )
        date_str = date_span.text.split(" ")[0]
        return datetime.strptime(date_str, "%d/%m/%Y").date()


if __name__ == "__main__":
    scraper = RokettoScraper()
    try:
        day = datetime.now().date()
        for i in range(6):
            print(scraper.scrape(day + timedelta(days=i)))
    except Exception as e:
        print(e)
        traceback.print_exc()

    time.sleep(100000)
