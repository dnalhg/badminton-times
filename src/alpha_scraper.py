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


class AlphaScraper:

    LOCATIONS = ["egerton", "auburn", "slough"]
    _SITE_URL = "https://alphabadminton.yepbooking.com.au/"
    _driver: Chrome

    def __init__(self):
        self._driver = create_chromedriver()

    def scrape(self, branch: str, day: date) -> ScrapingResult | None:
        page_source = self._get_page_source(branch, day)
        if page_source is None:
            return None

        soup = BeautifulSoup(page_source, "html.parser")
        table = soup.find("div", {"class": "schemaWrapperOuter"})
        available_cells = table.select('a[aria-label*="Available"]')

        available_start_times = set()
        for c in available_cells:
            label = c["aria-label"]
            parts = label.split("–")
            start = parts[0]
            hour = int(start.split(":")[0])
            if "pm" in start and hour < 12:
                hour += 12
            available_start_times.add(hour)

        available_start_times = sorted(available_start_times)
        return ScrapingResult(
            location="alpha",
            branch=branch,
            day=day,
            available_times=[(i, i + 1) for i in available_start_times],
        )

    def _get_curr_booking_date(self):
        wait = WebDriverWait(self._driver, 2)
        container = wait.until(
            expected_conditions.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'div[class="schemaFullContainer"]',
                )
            )
        )

        date_str = container.find_element(By.CSS_SELECTOR, "h3").text
        # Example: Friday, 28th Mar 2025
        # Remove the ordinal suffix (th, nd, rd, st) from the day
        day_part = date_str.split()[1]  # "28th"
        day_num = "".join(filter(str.isdigit, day_part))  # "28"

        # Reconstruct the date string without the ordinal suffix
        cleaned_date_str = date_str.replace(day_part, day_num)  # "Friday, 28 Mar 2025"

        # Parse using strptime with appropriate format
        return datetime.strptime(cleaned_date_str, "%A, %d %b %Y").date()

    def _close_popup(self):
        wait = WebDriverWait(self._driver, 2)
        try:
            close = wait.until(
                expected_conditions.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "button[title='Close']",
                    )
                )
            )

            close.click()
        except (TimeoutException, ElementNotInteractableException):
            pass

    def _get_page_source(self, location: str, day: date):
        if day < datetime.now().date():
            print(f"{day} is before today")
            return None
        wait = WebDriverWait(self._driver, 2)

        if self._driver.current_url != self._SITE_URL:
            self._driver.get(self._SITE_URL)
            self._close_popup()

        tabs = wait.until(
            expected_conditions.visibility_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "a[infotab_type]",
                )
            )
        )

        location_button = None
        for t in tabs:
            if location.lower() in t.text.lower():
                location_button = t
                break

        if location_button is None:
            print(f"Could not find button for $location")
            return None

        location_button.click()
        self._close_popup()

        curr_booking_date = self._get_curr_booking_date()
        while curr_booking_date != day:
            if curr_booking_date < day:
                # Press next
                next = wait.until(
                    expected_conditions.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "a[id='nextDateMover']",
                        )
                    )
                )
                next.click()
            else:
                # Press prev
                prev = wait.until(
                    expected_conditions.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "a[id='prevDateMover']",
                        )
                    )
                )
                prev.click()
            time.sleep(1)
            curr_booking_date = self._get_curr_booking_date()

        return self._driver.page_source


if __name__ == "__main__":
    scraper = AlphaScraper()
    try:
        day = datetime.strptime("2025-04-05", "%Y-%m-%d").date()
        for i in range(1):
            for location in scraper.LOCATIONS:
                print(scraper.scrape(location, day + timedelta(days=i)))
    except Exception as e:
        print(e)
        traceback.print_exc()

    time.sleep(100000)
