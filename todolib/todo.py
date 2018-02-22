import re
import datetime
from todolib import Util


class Todo:
    """Single Todo item"""

    _priority_regex = re.compile(r"\(([A-Z])\) ")
    _context_regex = re.compile(r"(?:^|\s+)(@\S+)")
    _project_regex = re.compile(r"(?:^|\s+)(\+\S+)")
    _done_regex = re.compile(r"^x (\d\d\d\d-\d\d-\d\d) ")
    _creation_date_regex = re.compile(r"^"
                                      r"(?:x \d\d\d\d-\d\d-\d\d )?"
                                      r"(?:\(\w\) )?"
                                      r"(\d\d\d\d-\d\d-\d\d)\s*")
    _due_date_regex = re.compile(r"\s*due:(\d\d\d\d-\d\d-\d\d)\s*")
    _rec_int_regex = re.compile(r"\s*rec:(\+?\d+[dwmy])\s*")
    _rec_int_parts_regex = re.compile(r"(\+)?(\d+)([dwmy])")

    PLHR = u"\N{HORIZONTAL ELLIPSIS}"
    _plhr_regex = re.compile(PLHR + "[ " + PLHR + "]*")

    def __init__(self, item, item_id):
        self.item_id = item_id
        self.update(item)

    def update(self, item):
        self.raw = item.strip()
        self.priority = Todo.scan_priority(item)
        self.contexts = Todo.scan_contexts(item)
        self.projects = Todo.scan_projects(item)
        self.done_date = Todo.scan_done_date(item)
        self.creation_date = Todo.scan_creation_date(item)
        self.due_date = Todo.scan_due_date(item)
        self.rec_int = Todo.scan_rec_int(item)

    @staticmethod
    def scan_contexts(item):
        return sorted(Todo._context_regex.findall(item))

    @staticmethod
    def scan_projects(item):
        return sorted(Todo._project_regex.findall(item))

    @staticmethod
    def scan_creation_date(item):
        match = Todo._creation_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def scan_due_date(item):
        match = Todo._due_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def scan_rec_int(item):
        match = Todo._rec_int_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def scan_priority(item):
        match = Todo._priority_regex.match(item)
        return match.group(1) if match else ""

    @staticmethod
    def scan_done_date(item):
        match = Todo._done_regex.match(item)
        return match.group(1) if match else ""

    @staticmethod
    def get_current_date(inc=0):
        return datetime.date.today() + datetime.timedelta(days=inc)

    @staticmethod
    def get_current_date_str(inc=0):
        return Todo.get_current_date(inc).isoformat()

    def __repr__(self):
        return repr({
            "raw": self.raw,
            "item_id": self.item_id,
            "priority": self.priority,
            "done_date": self.done_date,
            "creation_date": self.creation_date,
            "contexts": self.contexts,
            "projects": self.projects,
            "due_date": self.due_date,
            "rec_int": self.rec_int,
        })

    def change_priority(self, new_priority):
        self.priority = new_priority
        if new_priority:
            new_priority = "({}) ".format(new_priority)

        if re.search(self._priority_regex, self.raw):
            self.raw = re.sub(self._priority_regex, "{}".format(new_priority), self.raw)
        elif re.search(r"^x \d{4}-\d{2}-\d{2}", self.raw):
            self.raw = re.sub(r"^(x \d{4}-\d{2}-\d{2}) ", r"\1 {}".format(new_priority), self.raw)
        else:
            self.raw = "{}{}".format(new_priority, self.raw)
        self.update(self.raw)

    def is_done(self):
        if self.raw[0:2] == "x ":
            return True
        elif self.done_date == "":
            return False
        else:
            return True

    def set_done(self, done=True):
        if done:
            today = datetime.date.today()
            self.raw = "x " + today.isoformat() + " " + self.raw
            self.update(self.raw)
            if self.rec_int:
                (prefix, value, itype) = Todo._rec_int_parts_regex.match(self.rec_int).groups()
                value = int(value)
                date = self.get_due() if prefix == "+" else today
                return Util.date_add_interval(date, itype, value)
        else:
            self.raw = re.sub(Todo._done_regex, "", self.raw)
            self.update(self.raw)

    def get_status(self, sdate):
        if self.is_done(): return "done"
        if self.due_date:
            if self.due_date < sdate: return "overdue"
            elif self.due_date == sdate: return "due"
        return "todo"

    def is_due(self, sdate):
        return not self.is_done() and self.due_date and self.due_date <= sdate

    def set_due(self, due):
        if not type(due) is datetime.date: due = due.date()
        text = " due:" + due.isoformat()
        if self.due_date: self.raw = re.sub(Todo._due_date_regex, text + " ", self.raw)
        else: self.raw += text
        self.update(self.raw)

    def get_due(self):
        return datetime.datetime.strptime(self.due_date, "%Y-%m-%d").date() if self.due_date else None

    def add_creation_date(self):
        if self.creation_date == "":
            p = "({0}) ".format(self.priority) if self.priority != "" else ""
            self.update("{0}{1} {2}".format(p, datetime.date.today(), self.raw.replace(p, "")))

    def get_desc(self):
        PLHR = u" \N{HORIZONTAL ELLIPSIS} "
        res = self.raw
        res = re.sub(Todo._due_date_regex, PLHR, res)
        res = re.sub(Todo._rec_int_regex, PLHR, res)
        res = re.sub(Todo._context_regex, PLHR, res)
        res = re.sub(Todo._plhr_regex, PLHR, res)
        return res.strip(PLHR)
