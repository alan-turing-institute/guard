# A range of dates, used to control sampling periods
class DateRange(object):
    def __init__(self, start_year, end_year):
        assert start_year < end_year
        self.start_year = start_year
        self.end_year = end_year
        self.label = self._create_label()

    @classmethod
    def from_string(cls, string):
        # Get dates in AD/BC format from string
        dates = string.split('-')

        # Change into integer representation
        for i, date in enumerate(dates):
            if date == '0':
                dates[i] = 0
            elif date[-2:] == 'BC':
                dates[i] = int(date[:-2])*-1
            else:
                dates[i] = int(date[:-2])

        return cls(*dates)

    def _create_label(self):
        if self.start_year < 0:
            label = '{:d}BC-'.format(abs(self.start_year))
        elif self.start_year == 0:
            label = '{:d}-'.format(abs(self.start_year))
        else:
            label = '{:d}AD-'.format(abs(self.start_year))

        if self.end_year < 0:
            label += '{:d}BC'.format(abs(self.end_year))
        elif self.end_year == 0:
            label += '{:d}'.format(abs(self.end_year))
        else:
            label += '{:d}AD'.format(abs(self.end_year))

        return label

    def __str__(self):
        return self.label

    def __hash__(self):
        return hash(self.label)

    def __eq__(self, other):
        if isinstance(other, DateRange):
            return (self.start_year == other.start_year
                    and self.end_year == other.end_year)
        elif isinstance(other, str):
            return self.label == other
        else:
            return False

    # Determine whether a year is within the date range
    def is_within(self, year):
        if year >= self.start_year and year < self.end_year:
            return True
        else:
            return False


# Date ranges of cities data
cities_date_ranges = [
    DateRange(-2500, -1000),
    DateRange(-1000, 0),
    DateRange(0, 500),
    DateRange(500, 1000),
    DateRange(700, 850),
    DateRange(850, 1000),
    DateRange(1000, 1100),
    DateRange(1100, 1200),
    DateRange(1200, 1300),
    DateRange(1300, 1400),
    DateRange(1400, 1500)]

# Default date ranges for imperial density eras
imperial_density_date_ranges = [
    DateRange(-1500, -500),
    DateRange(-500, 500),
    DateRange(500, 1500)]


class InvalidDateRange(Exception):
    pass
