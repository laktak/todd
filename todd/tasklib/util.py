
import re
import datetime


def _get_today():
    return datetime.date.today()


class Util:

    _interval_parts_regex = re.compile(r"([+-])?(\d+)([dwmy]?)")
    delta0 = datetime.timedelta(days=0)
    delta1 = datetime.timedelta(days=1)
    delta7 = datetime.timedelta(days=7)
    delta30 = datetime.timedelta(days=30)
    WDAY = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    @staticmethod
    def get_today(inc=0):
        return _get_today() + datetime.timedelta(days=inc)

    @staticmethod
    def get_next_monday(inc=0):
        res = _get_today()
        return res + datetime.timedelta(days=7 - res.weekday() + inc)

    @staticmethod
    def get_today_str(inc=0):
        return Util.get_today(inc).isoformat()

    @staticmethod
    def _date_add_months(date, value):
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
    def date_add_interval(date, t, value):
        if t == "d" or t == "": return date + datetime.timedelta(days=value)
        elif t == "w": return date + datetime.timedelta(days=value * 7)
        elif t == "m": return Util._date_add_months(date, value)
        elif t == "y": return Util._date_add_months(date, value * 12)
        else: return date

    @staticmethod
    def _get_next_weekday(day, *, today=_get_today()):
        delta = day - today.weekday()
        if delta <= 0: delta += 7
        return today + datetime.timedelta(days=delta)

    @staticmethod
    def _parse_relative_date(text, *, today=_get_today()):
        text = text.strip().lower()
        text2 = text[:2]
        for idx, day in enumerate(Util.WDAY):
            if text2 == day[:2]:
                return Util._get_next_weekday(idx, today=today)
        if text[:3] == 'tod': return Util.get_today()  # today
        elif text == 'to': return Util.get_today(1)  # tomorrow
        elif text2 == 'ye': return Util.get_today(-1)  # yesterday
        try:
            delta = int(text)
            return today + datetime.timedelta(days=delta)
        except ValueError:
            pass

    @staticmethod
    def mod_date_by(date, text, *, today=_get_today()):
        # try relative date
        date2 = Util._parse_relative_date(text, today=today)
        if date2: return date2
        # try interval
        (prefix, value, itype) = Util._interval_parts_regex.match(text).groups()
        value = int(value)
        mod = -1 if prefix == "-" else 1
        return Util.date_add_interval(date, itype, value * mod)

    @staticmethod
    def define_keys(command_map, key_bindings, mappings):
        for (name, final) in mappings:
            keys = key_bindings.getKeyBinding(name)
            for key in keys:
                command_map[key] = final
        return command_map

    @staticmethod
    def get_date_name(date, *, today=_get_today()):
        if date is None: return "later"
        v = date - today
        if v < Util.delta0:
            if v == -Util.delta1: return "yesterday"
            elif v >= -Util.delta7: return "last " + Util.WDAY[date.weekday()][:3]
            elif v >= -Util.delta30: return "{0} days ago".format(-v.days)
            return date.isoformat()
        elif v == Util.delta0: return "today"
        elif v == Util.delta1: return "tomorrow"
        elif v <= Util.delta7: return Util.WDAY[date.weekday()]
        elif v <= Util.delta30: return "in {0} days".format(v.days)
        else: return date.isoformat()
