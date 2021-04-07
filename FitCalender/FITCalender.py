#  Copyright (c) 2021. fit&healthy 365

import calendar
from datetime import datetime


class FITCalendar(calendar.HTMLCalendar):
    """"
    Creates a monthly calendar to track date events
    """

    def __init__(self,
                 current_day: int,
                 event_dates: list = None,
                 event_color: str = '#9e1f63'):
        super().__init__(calendar.SUNDAY)
        self._current_day = current_day
        self._event_dates = event_dates if event_dates else list()
        self._event_color = event_color

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="col-md-1 %s">%s</th>' % (  # col-md-1 class added for bootstrap
            self.cssclasses_weekday_head[day], calendar.day_abbr[day])

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        return self.make_day_cell(day, weekday, self.day_string(day))

    def make_day_cell(self, day, weekday, day_string):
        if day == 0:
            # day outside month
            return '<td class="%s" bg>&nbsp;</td>' % self.cssclass_noday
        elif day in self._event_dates:
            return '<td class="%s" bgcolor="%s">%s</td>' % (
                self.cssclasses[weekday],
                self._event_color,
                day_string)
        else:
            return '<td class="%s">%s</td>' % (
                self.cssclasses[weekday],
                day_string)

    def day_string(self, day):
        if day == self._current_day:
            day_string = '<strong>%d</strong>' % day
        else:
            day_string = '%d' % day
        return day_string

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table class="table %s">' % (  # added table class for bootstrap
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


def calender_html(year: int = None, month: int = None, events: list = None) -> 'html':
    current_date = datetime.today()
    if not year:
        year = current_date.year
    if not month:
        month = current_date.month
    if current_date.year == year and current_date.month == month:
        current_day = current_date.day
    else:
        current_day = None
    if events:
        days = [d.day for d in events if d.month == month and d.year == year]
    else:
        days = None
    html_cal = FITCalendar(current_day, days)
    month_cal = html_cal.formatmonth(year, month)
    return month_cal
