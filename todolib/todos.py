#!/usr/bin/env python
# coding=utf-8
import re
import random
from todolib.todo import Todo


class Todos:
    """Todo items"""

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
                done = Todos.filter_done(self.todo_items)
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

    def __getitem__(self, index):
        return self.todo_items[index]

    def __repr__(self):
        return repr([i for i in self.todo_items])

    def create_todo(self, todo, index):
        return Todo(todo, index)

    def parse_raw_entries(self, raw_items):
        self.todo_items = [
            self.create_todo(todo, index)
            for index, todo in enumerate(raw_items) if todo.strip() != ""]

    def update_raw_indices(self):
        for index, todo in enumerate(self.todo_items):
            todo.raw_index = index

    def all_contexts(self):
        return sorted(set([context for todo in self.todo_items for context in todo.contexts]))

    def all_projects(self):
        return sorted(set([project for todo in self.todo_items for project in todo.projects]))

    def get_items_sorted(self, sort_by):
        def due_prio(todo):
            res = todo.due_date + todo.raw
            if not res: res = "z"
            if todo.is_done(): res = "z" + res
            return res
        def prio(todo):
            return todo.raw

        if sort_by == "due": return sorted(self.todo_items, key=due_prio)
        elif sort_by == "prio": return sorted(self.todo_items, key=prio)

    @staticmethod
    def filter_due(items, date):
        return [t for t in items if t.is_due(date)] if items else []

    @staticmethod
    def filter_pending(items):
        return [t for t in items if not t.is_done()] if items else []

    @staticmethod
    def filter_done(items):
        return [t for t in items if t.is_done()] if items else []

    @staticmethod
    def filter_context(items, context):
        return [item for item in items if context in item.contexts]

    @staticmethod
    def search(items, search_string):
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
        for t in items:
            match = r.search(t.raw)
            if match:
                t.search_matches = match.groups()
                results.append(t)
        return results

