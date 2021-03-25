#  Copyright (c) 2021. fit&healthy 365

import calendar
from datetime import datetime


class FITCalendar(calendar.HTMLCalendar):

    def __init__(self, _date: datetime, _color: str):
        super().__init__(calendar.SUNDAY)
        self._date = _date
        self._color = _color

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            # day outside month
            return '<td class="%s" bg>&nbsp;</td>' % self.cssclass_noday
        elif self._date and day == self._date.day:
            return '<td class="%s" bgcolor="%s">%d</td>' % (self.cssclasses[weekday], self._color, day)
        else:
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table class="table table-hover %s">' % (
            self.cssclass_month))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


def calender_html(select_date: datetime = None, select_color='#9e1f63') -> 'html':
    if not select_date:
        select_date = datetime.today()
    html_cal = FITCalendar(select_date, select_color,)
    month_cal = html_cal.formatmonth(select_date.year, select_date.month)
    return month_cal
