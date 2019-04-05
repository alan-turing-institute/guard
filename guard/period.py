"""
Agricultural period class and periods.
"""


class Period(object):
    """
    Agricultural period class.

    Args:
        active_from (int): The step number at which communities in this period
            become agriculturally active.
    """
    def __init__(self, active_from):
        self.active_from = active_from

    def is_active(self, step_number):
        """
        Determine whether communities belonging to this period are currently
        active.

        Args:
            step_number (int): The current step number.

        Returns:
            (bool): True if communities in this period are agriculturally
                active, False otherwise.
        """
        return step_number >= self.active_from


"""
Agricultural from 1500BCE (the beginning)
"""
agri1 = Period(0)
"""
Agricultural from 300CE
"""
agri2 = Period(900)
"""
Agricultural from 700CE
"""
agri3 = Period(1100)
