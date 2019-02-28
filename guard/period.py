class Period(object):
    def __init__(self, active_from):
        self.active_from = active_from

    def is_active(self, step_number):
        return step_number >= self.active_from


# Agricultural from 1500BCE (the beginning)
agri1 = Period(0)
# Agricultural from 300CE
agri2 = Period(900)
# Agricultural from 700CE
agri3 = Period(1100)
