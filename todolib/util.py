
import re
import datetime

class Util:

    _interval_parts_regex = re.compile(r'([+-])?(\d+)([dwmy])')

    @staticmethod
    def date_add_interval(date, t, value):
        if t == 'd': return date + datetime.timedelta(days=value)
        elif t == 'w': return date + datetime.timedelta(days=value * 7)
        elif t == 'm': return Util.date_add_months(date, value)
        elif t == 'y': return Util.date_add_months(date, value * 12)
        else: return date

    @staticmethod
    def date_add_months(date, value):
        (y, m, d) = (date.year, date.month, date.day)
        m += value
        while m > 12:
            y += 1
            m -= 12
        while m < 1:
            y -= 1
            m += 12
        d_last = datetime.date(y, m, 1) + datetime.timedelta(days=31)
        d_last = d_last - datetime.timedelta(days=d_last.day)
        return datetime.date(y, m, d) if d < d_last.day else d_last

    @staticmethod
    def scan_interval(date, text):
        (prefix, value, itype) = Util._interval_parts_regex.match(text).groups()
        value = int(value)
        mod = -1 if prefix == '-' else 1
        return Util.date_add_interval(date, itype, value * mod)
