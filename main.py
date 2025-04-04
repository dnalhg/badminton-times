import argparse
from datetime import datetime, date, timedelta
import multiprocessing as mp
from src.alpha_scraper import AlphaScraper
from src.roketto_scraper import RokettoScraper


def _generate_date_range(start_date: date, end_date: date):
    days = int((end_date - start_date).days)
    for n in range(days + 1):
        yield start_date + timedelta(n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="The date to start scraping from in YYYY-mm-dd format",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=True,
        help="The date to end scraping from (inclusive) in YYYY-mm-dd format",
    )
    args = parser.parse_args()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()

    if start_date > end_date:
        print(f"Start date {start_date} > End date {end_date}")

    def _scrape_alpha():
        results = []
        scraper = AlphaScraper()
        for day in _generate_date_range(start_date, end_date):
            for loc in scraper.LOCATIONS:
                res = scraper.scrape(loc, day)
                if res is not None:
                    results.append(res)

        scraper.close()
        return results

    def _scrape_roketto():
        results = []
        scraper = RokettoScraper()
        for day in _generate_date_range(start_date, end_date):
            res = scraper.scrape(day)
            if res is not None:
                results.append(res)

        scraper.close()
        return results

    with mp.Pool(2) as pool:
        alpha_results = pool.apply_async(_scrape_alpha)
        roketto_results = pool.apply_async(_scrape_roketto)

        pool.close()
        pool.join()

    all_results = sorted(
        alpha_results.get() + roketto_results.get(), key=lambda res: res.day
    )
    for r in all_results:
        print(r)
