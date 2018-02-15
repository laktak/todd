#!/usr/bin/env python
# coding=utf-8
import re
import random
from datetime import date


class Todo:
    """Single Todo item"""
    _priority_regex = re.compile(r'\(([A-Z])\) ')

    def __init__(self, item, index,
                 colored="", priority="", contexts=[], projects=[],
                 creation_date="", due_date="", completed_date=""):
        self.raw = item.strip()
        self.raw_index = index
        self.creation_date = creation_date
        self.priority = priority
        self.contexts = contexts
        self.projects = projects
        self.due_date = due_date
        self.completed_date = completed_date
        self.colored = self.highlight()
        # self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

    def update(self, item):
        self.raw = item.strip()
        self.priority = Todos.priority(item)
        self.contexts = Todos.contexts(item)
        self.projects = Todos.projects(item)
        self.creation_date = Todos.creation_date(item)
        self.due_date = Todos.due_date(item)
        self.completed_date = Todos.completed_date(item)
        self.colored = self.highlight()
        # self.colored_length = TerminalOperations.length_ignoring_escapes(self.colored)

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
        self.raw = re.sub(Todos._completed_regex, "", self.raw)
        self.completed_date = ""
        self.update(self.raw)

    def add_creation_date(self):
        if self.creation_date == "":
            p = "({0}) ".format(self.priority) if self.priority != "" else ""
            self.update("{0}{1} {2}".format(p, date.today(), self.raw.replace(p, "")))


class Todos:
    """Todo items"""
    _context_regex = re.compile(r'(?:^|\s+)(@\S+)')
    _project_regex = re.compile(r'(?:^|\s+)(\+\S+)')
    _creation_date_regex = re.compile(r'^'
                                      r'(?:x \d\d\d\d-\d\d-\d\d )?'
                                      r'(?:\(\w\) )?'
                                      r'(\d\d\d\d-\d\d-\d\d)\s*')
    _due_date_regex = re.compile(r'\s*due:(\d\d\d\d-\d\d-\d\d)\s*')
    _priority_regex = re.compile(r'\(([A-Z])\) ')
    _completed_regex = re.compile(r'^x (\d\d\d\d-\d\d-\d\d) ')

    def __init__(self, todo_items, file_path, archive_path):
        self.file_path = file_path
        self.archive_path = archive_path
        self.update(todo_items)

    def reload_from_file(self):
        with open(self.file_path, "r") as todotxt_file:
            self.update(todotxt_file.readlines())

    def save(self):
        with open(self.file_path, "w") as todotxt_file:
            for t in self.todo_items:
                todotxt_file.write(t.raw + '\n')

    def archive_done(self):
        if self.archive_path is not None:
            with open(self.archive_path, "a") as donetxt_file:
                done = self.done_items()
                for t in done:
                    donetxt_file.write(t.raw + '\n')
                    self.todo_items.remove(t)

            self.save()
            return True

        return False

    def update(self, todo_items):
        self.parse_raw_entries(todo_items)

    def append(self, item, add_creation_date=True):
        self.insert(len(self.todo_items), item, add_creation_date)
        return len(self.todo_items) - 1

    def insert(self, index, item, add_creation_date=True):
        self.todo_items.insert(index, self.create_todo(item, index))
        self.update_raw_indices()
        newtodo = self.todo_items[index]
        if add_creation_date and newtodo.creation_date == "":
            newtodo.add_creation_date()
        return index

    def delete(self, index):
        del self.todo_items[index]
        self.update_raw_indices()

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def next(self):
        self.index = self.index + 1
        if self.index == len(self.todo_items):
            raise StopIteration
        return self.todo_items[self.index]

    def __len__(self):
        return len(self.todo_items)

    def pending_items(self):
        return [t for t in self.todo_items if not t.is_complete()]

    def done_items(self):
        return [t for t in self.todo_items if t.is_complete()]

    def pending_items_count(self):
        return len(self.pending_items())

    def done_items_count(self):
        return len(self.done_items())

    def __getitem__(self, index):
        return self.todo_items[index]

    def __repr__(self):
        return repr([i for i in self.todo_items])

    def create_todo(self, todo, index):
        return Todo(todo, index,
                    contexts=Todos.contexts(todo),
                    projects=Todos.projects(todo),
                    priority=Todos.priority(todo),
                    creation_date=Todos.creation_date(todo),
                    due_date=Todos.due_date(todo),
                    completed_date=Todos.completed_date(todo))

    def parse_raw_entries(self, raw_items):
        self.todo_items = [
            self.create_todo(todo, index)
            for index, todo in enumerate(raw_items) if todo.strip() != ""]

    def update_raw_indices(self):
        for index, todo in enumerate(self.todo_items):
            todo.raw_index = index

    @staticmethod
    def contexts(item):
        return sorted(Todos._context_regex.findall(item))

    @staticmethod
    def projects(item):
        return sorted(Todos._project_regex.findall(item))

    @staticmethod
    def creation_date(item):
        match = Todos._creation_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def due_date(item):
        match = Todos._due_date_regex.search(item)
        return match.group(1) if match else ""

    @staticmethod
    def priority(item):
        match = Todos._priority_regex.match(item)
        return match.group(1) if match else ""

    @staticmethod
    def completed_date(item):
        match = Todos._completed_regex.match(item)
        return match.group(1) if match else ""

    def all_contexts(self):
        # Nested Loop
        # all_contexts = []
        # for item in self.raw_items:
        #   for found_context in self.contexts(item):
        #     if found_context not in all_contexts:
        #       all_contexts.append(found_context)
        # return all_contexts

        # List comprehension
        # return sorted(set( [found_context for item in self.raw_items for found_context in self.contexts(item)] ))

        # Join all items and use one regex.findall
        # return sorted(set( Todos._context_regex.findall(" ".join(self.raw_items))))

        return sorted(set([context for todo in self.todo_items for context in todo.contexts]))

    def all_projects(self):
        # List comprehension
        # return sorted(set( [project for item in self.raw_items for project in self.projects(item)] ))

        # Join all items and use one regex.findall
        # return sorted(set( Todos._project_regex.findall(" ".join(self.raw_items))))

        return sorted(set([project for todo in self.todo_items for project in todo.projects]))

    def sorted(self, reversed_sort=False):
        self.todo_items.sort(key=lambda todo: todo.raw, reverse=reversed_sort)

    def sorted_reverse(self):
        self.sorted(reversed_sort=True)

    def sorted_raw(self):
        self.todo_items.sort(key=lambda todo: todo.raw_index)

    def swap(self, first, second):
        """
        Swap items indexed by *first* and *second*.

        Out-of-bounds situations are handled by wrapping.
        """
        if second < first:
            second, first = first, second

        n_items = len(self.todo_items)

        if first < 0:
            first += n_items

        if second >= n_items:
            second = n_items - second

        self.todo_items[first], self.todo_items[second] = self.todo_items[second], self.todo_items[first]

    def filter_context(self, context):
        return [item for item in self.todo_items if context in item.contexts]

    def filter_project(self, project):
        return [item for item in self.todo_items if project in item.projects]

    def filter_context_and_project(self, context, project):
        return [item for item in self.todo_items if project in item.projects and context in item.contexts]

    def filter_contexts_and_projects(self, contexts, projects):
        return [item for item in self.todo_items if set(projects) & set(item.projects) or set(contexts) & set(item.contexts)]

    def search(self, search_string):
        search_string = re.escape(search_string)
        # print(search_string)
        ss = []
        substrings = search_string.split("\\")
        for index, substring in enumerate(substrings):
            s = ".*?".join(substring)
            # s.replace(" .*?", " ")
            if 0 < index < len(substrings) - 1:
                s += ".*?"
            ss.append(s)
        # print(repr(ss))
        search_string_regex = '^.*('
        search_string_regex += "\\".join(ss)
        search_string_regex += ').*'
        # print(search_string_regex)

        r = re.compile(search_string_regex, re.IGNORECASE)
        results = []
        for t in self.todo_items:
            match = r.search(t.raw)
            if match:
                t.search_matches = match.groups()
                results.append(t)
        return results

