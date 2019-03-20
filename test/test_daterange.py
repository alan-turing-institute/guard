from guard import daterange


class TestDateRange(object):
    def test_label(self):
        date_range = daterange.DateRange(-5, 5)

        assert str(date_range) == '5BC-5AD'

    def test_equivalence(self):
        date_range = daterange.DateRange(-5, 5)
        date_range2 = daterange.DateRange(-5, 5)

        assert date_range == date_range2
        assert date_range == '5BC-5AD'

    def test_hash(self):
        date_range = daterange.DateRange(0, 500)
        test_dict = {date_range: 'test'}

        assert test_dict['0-500AD'] == 'test'

    def test_from_string(self):
        date_range_1 = daterange.DateRange(-500, 200)
        date_range_2 = daterange.DateRange.from_string('500BC-200AD')

        assert date_range_1 == date_range_2
