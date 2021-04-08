#  Copyright (c) 2021. fit&healthy 365

import calendar
from datetime import datetime

from flask import url_for


def calender_html(month: int, year: int, events: list = None):
    def make_button(action_type, day, day_string):
        action = '<input type="hidden" name="action" value="%s">' % action_type
        form = ['<form action="%s" method="post">' % url_for('challenge_calendar_submit'),
                '</form>']
        button = ['<button'
                  ' type="submit"'
                  ' value="%s"'
                  ' name="day">' % day,
                  '</button>']
        day_string = form[0] + action + button[0] + day_string + button[1] + form[1]
        return day_string

    class FITCalendar(calendar.HTMLCalendar):
        """"
        Creates a monthly calendar to track date events
        """

        def __init__(self,
                     current_day: int,
                     event_dates: list = None,
                     event_color='#9e1f63'):
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

        def day_string(self, day):
            return '<strong>%d</strong>' % day \
                if day == self._current_day \
                else '%d' % day

        def make_day_cell(self, day, weekday, day_string):
            if day == 0:  # day outside month
                return '<td class="%s" bg>&nbsp;</td>' % self.cssclass_noday
            elif day in self._event_dates:
                button = make_button("delete", day, day_string)
                return '<td class="%s" bgcolor="%s">%s</td>' % (
                    self.cssclasses[weekday],
                    self._event_color,
                    button)
            else:
                button = make_button("insert", day, day_string)
                return '<td class="%s">%s</td>' % (
                    self.cssclasses[weekday],
                    button)

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

    current_date = datetime.today()

    if events:
        completed_days = events_during(events, year, month)
    else:
        completed_days = None

    if current_date.year == year and current_date.month == month:
        today = current_date.day
    else:
        today = None
    html_calender = FITCalendar(today, completed_days)
    return html_calender.formatmonth(year, month)


def events_during(events, year, month):
    completed_days = [d.day for d in events if d.month == month and d.year == year]
    return completed_days
