import os
import re
from todolib import Todo


class Todos:
    """Todo items"""

    def __init__(self, text_items):
        self.set_items(text_items or [])

    @staticmethod
    def open_file(file_path, archive_path=None):
        todos = Todos(None)
        todos.file_path = file_path
        if archive_path: todos.archive_path = archive_path
        else: todos.archive_path = os.path.join(os.path.dirname(file_path), "done.txt")
        todos.reload()
        return todos

    def reload(self):
        with open(self.file_path, "r", encoding="utf-8") as todotxt_file:
            self.set_items(todotxt_file.readlines())

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as todotxt_file:
            for t in self._items:
                todotxt_file.write(t.raw + "\n")

    def archive_done(self):
        with open(self.archive_path, "a", encoding="utf-8") as donetxt_file:
            done = Todos.filter_done(self._items)
            for t in done:
                donetxt_file.write(t.raw + "\n")
                self._items.remove(t)
        self.save()

    def set_items(self, text_items):
        self._items = [
            Todo(todo, index)
            for index, todo in enumerate(text_items) if todo.strip() != ""]

    def update_raw_indices(self):
        for index, todo in enumerate(self._items):
            todo.raw_index = index

    def append(self, item):
        self.insert(len(self._items), item)
        self.update_raw_indices()
        return len(self._items) - 1

    def insert(self, index, item):
        self._items.insert(index, Todo(item, index))
        self.update_raw_indices()

    def delete(self, index):
        del self._items[index]
        self.update_raw_indices()

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index = self.index + 1
        if self.index == len(self._items):
            raise StopIteration
        return self._items[self.index]

    def next(self):
        self.index = self.index + 1
        if self.index == len(self._items):
            raise StopIteration
        return self._items[self.index]

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __repr__(self):
        return repr([i for i in self._items])

    def all_contexts(self):
        return sorted(set([context for todo in self._items for context in todo.contexts]))

    def all_projects(self):
        return sorted(set([project for todo in self._items for project in todo.projects]))

    def get_items(self):
        return self._items

    def get_items_sorted(self, sort_by):

        def due_prio(todo):
            res = todo.due_date
            if not res: res = "9999"
            res += todo.raw
            if not res: res = "z"
            if todo.is_done(): res = "z" + res
            return res

        def prio(todo):
            return todo.raw

        if sort_by == "due": return sorted(self._items, key=due_prio)
        elif sort_by == "prio": return sorted(self._items, key=prio)

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
    def prep_search(search_string):
        search_list = [x for x in [x.strip() for x in search_string.split(" ")] if x != ""]
        if not search_list: return None
        exp1 = "".join(["(?=.*(" + re.escape(item) + "))" for item in search_list])
        exp2 = "(" + "|".join([re.escape(item) for item in search_list]) + ")"
        return (re.compile(exp1, re.IGNORECASE), re.compile(exp2, re.IGNORECASE))

    @staticmethod
    def search(search, items):
        if not search: return items
        return [item for item in items if search[0].search(item.raw)]

    @staticmethod
    def get_search_highlight(search, text):
        try:
            color_list = search[1].split(text)
            matches = search[0].search(text).groups()
            for index, w in enumerate(color_list):
                if w in matches: color_list[index] = ("search_match", w)
            return color_list
        except Exception:
            return text
