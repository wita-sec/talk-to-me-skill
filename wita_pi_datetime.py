#!/usr/bin/python

"""date and time methods for the Picroft skills
"""

import datetime

class pi_datetime:
    """ provides methods around date and time
        e.g. diff between two dates
        more methods to come...

    """
    def __init__(self):
        self.iso_format = "%Y-%m-%d %H:%M:%S"

    ############################################################################

    def diff(self, date_from, date_to):
        """ calculates difference between the two dates
            dates need to be formatted as string in self.iso_format
            when a date is "now", the current date will be used.
            The difference is returned in terms of days.
            rc = 0 no errors, else some error occured
            rc_msg = return message
            rc_diff = difference between dates as int
        """
        rc = 0
        rc_msg = "success"
        rc_diff = 0
        if date_from == 'now':
            dt_dt_from = datetime.datetime.now()
            dt_str_from = dt_dt_from.strftime(self.iso_format)
        else:
            dt_str_from = date_from

        if date_to == 'now':
            dt_dt_to = datetime.datetime.now()
            dt_str_to = dt_dt_to.strftime(self.iso_format)
        else:
            dt_str_to = date_to

        dt_from = datetime.datetime.strptime(dt_str_from, self.iso_format)
        dt_to   = datetime.datetime.strptime(dt_str_to,   self.iso_format)
        rc_diff = ((dt_from - dt_to).days)
        return rc, rc_msg, rc_diff

# class pi_datetime
############################################################################
