#!/usr/bin/env python
# coding=utf-8
import re
import random
from datetime import date


class Todo:
    """Single Todo item"""

    _context_regex = re.compile(r'(?:^|\s+)(@\S+)')
    _project_regex = re.compile(r'(?:^|\s+)(\+\S+)')
    _creation_date_regex = re.compile(r'^'
                                      r'(?:x \d\d\d\d-\d\d-\d\d )?'
                                      r'(?:\(\w\) )?'
                                      r'(\d\d\d\d-\d\d-\d\d)\s*')
    _due_date_regex = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
    _priority_regex = re.compile(r'\(([A-Z])\) ')
    _completed_regex = re.compile(r'^x (\d\d\d\d-\d\d-\d\d) ')

    def __init__(self, item, index):
        self.update(item)
        self.raw_index = index

    def update(self, item):
        self.raw = item.strip()
        self.priority = Todo.scan_priority(item)
        self.contexts = Todo.scan_contexts(item)
        self.projects = Todo.scan_projects(item)
        self.creation_date = Todo.scan_creation_date(item)
        self.due_date = Todo.scan_due_date(item)
        self.completed_date = Todo.scan_completed_date(item)
        self.colored = self.highlight()
        # self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

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
    def scan_priority(item):
        match = Todo._priority_regex.match(item)
        return match.group(1) if match else ""

    @staticmethod
    def scan_completed_date(item):
        match = Todo._completed_regex.match(item)
        return match.group(1) if match else ""

    def __repr__(self):
        return repr({
            "raw": self.raw,
            "colored": self.colored,
            "raw_index": self.raw_index,
            "priority": self.priority,
            "contexts": self.contexts,
            "projects": self.projects,
            "creation_date": self.creation_date,
            "due_date": self.due_date,
            "completed_date": self.completed_date
        })

    def highlight(self, line="", show_due_date=True, show_contexts=True, show_projects=True):
        colored = self.raw if line == "" else line
        color_list = [colored]

        if colored[:2] == "x ":
            color_list = ('completed', color_list)
        else:
            words_to_be_highlighted = self.contexts + self.projects
            if self.due_date:
                words_to_be_highlighted.append("due:" + self.due_date)
            if self.creation_date:
                words_to_be_highlighted.append(self.creation_date)

            if words_to_be_highlighted:
                color_list = re.split("(" + "|".join([re.escape(w) for w in words_to_be_highlighted]) + ")", self.raw)
                for index, w in enumerate(color_list):
                    if w in self.contexts:
                        color_list[index] = ('context', w) if show_contexts else ''
                    elif w in self.projects:
                        color_list[index] = ('project', w) if show_projects else ''
                    elif w == "due:" + self.due_date:
                        color_list[index] = ('due_date', w) if show_due_date else ''
                    elif w == self.creation_date:
                        color_list[index] = ('creation_date', w)

            if self.priority and self.priority in "ABCDEF":
                color_list = ("priority_{0}".format(self.priority.lower()), color_list)
            else:
                color_list = ("plain", color_list)

        return color_list

    def highlight_search_matches(self, line=""):
        colored = self.raw if line == "" else line
        color_list = [colored]
        if self.search_matches:
            color_list = re.split("(" + "|".join([re.escape(match) for match in self.search_matches]) + ")", self.raw)
            for index, w in enumerate(color_list):
                if w in self.search_matches:
                    color_list[index] = ('search_match', w)
        return color_list

    def change_priority(self, new_priority):
        self.priority = new_priority
        if new_priority:
            new_priority = '({}) '.format(new_priority)

        if re.search(self._priority_regex, self.raw):
            self.raw = re.sub(self._priority_regex, '{}'.format(new_priority), self.raw)
        elif re.search(r'^x \d{4}-\d{2}-\d{2}', self.raw):
            self.raw = re.sub(r'^(x \d{4}-\d{2}-\d{2}) ', r'\1 {}'.format(new_priority), self.raw)
        else:
            self.raw = '{}{}'.format(new_priority, self.raw)
        self.update(self.raw)

    def is_complete(self):
        if self.raw[0:2] == "x ":
            return True
        elif self.completed_date == "":
            return False
        else:
            return True

    def complete(self):
        today = date.today()
        self.raw = "x {0} ".format(today) + self.raw
        self.completed_date = "{0}".format(today)
        self.update(self.raw)

    def incomplete(self):
        self.raw = re.sub(Todo._completed_regex, "", self.raw)
        self.completed_date = ""
        self.update(self.raw)

    def add_creation_date(self):
        if self.creation_date == "":
            p = "({0}) ".format(self.priority) if self.priority != "" else ""
            self.update("{0}{1} {2}".format(p, date.today(), self.raw.replace(p, "")))
