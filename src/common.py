from datetime import date


class ScrapingResult:
    location: str
    branch: str
    day: date
    available_times: list[tuple[int, int]]

    def __init__(
        self,
        location: str,
        branch: str,
        day: date,
        available_times: list[tuple[int, int]],
    ):
        self.location = location
        self.branch = branch
        self.day = day
        self.available_times = available_times

        self._cached_time_ranges = None

    def __repr__(self):
        return f"{self.location} {self.branch} {self.day.day}/{self.day.month} ({self.day.strftime('%A')}) : {self.get_available_time_ranges()}"

    def get_available_time_ranges(self):
        if self._cached_time_ranges is None:
            self._compute_and_cache_time_ranges()

        return self._cached_time_ranges

    def _compute_and_cache_time_ranges(self):
        times_sorted = sorted(self.available_times, key=lambda r: r[0])
        time_ranges = []

        if len(times_sorted) <= 0:
            self._cached_time_ranges = []
            return

        curr_start = times_sorted[0][0]
        curr_end = times_sorted[0][1]
        for interval in times_sorted[1:]:
            if interval[0] == curr_end:
                # Extend the current interval
                curr_end = interval[1]
            else:
                # Start a new interval
                time_ranges.append((curr_start, curr_end))
                curr_start = interval[0]
                curr_end = interval[1]
        time_ranges.append((curr_start, curr_end))

        self._cached_time_ranges = time_ranges
