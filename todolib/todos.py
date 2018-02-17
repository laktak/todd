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
        return Todo(todo, index)

    def parse_raw_entries(self, raw_items):
        self.todo_items = [
            self.create_todo(todo, index)
            for index, todo in enumerate(raw_items) if todo.strip() != ""]

    def update_raw_indices(self):
        for index, todo in enumerate(self.todo_items):
            todo.raw_index = index

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
        # return sorted(set( Todo._context_regex.findall(" ".join(self.raw_items))))

        return sorted(set([context for todo in self.todo_items for context in todo.contexts]))

    def all_projects(self):
        # List comprehension
        # return sorted(set( [project for item in self.raw_items for project in self.projects(item)] ))

        # Join all items and use one regex.findall
        # return sorted(set( Todo._project_regex.findall(" ".join(self.raw_items))))

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

