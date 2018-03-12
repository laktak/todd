import os
import re
import watchdog.events
import watchdog.observers
from todd.tasklib import Task, Util


class Tasklist:

    def __init__(self, text_items):
        self.next_id = 1
        self.set_text_items(text_items or [])

    @staticmethod
    def open_file(file_path, archive_path=None):
        tasklist = Tasklist(None)
        tasklist.file_path = file_path
        if archive_path: tasklist.archive_path = archive_path
        else: tasklist.archive_path = os.path.join(os.path.dirname(file_path), "done.txt")
        tasklist.reload()
        return tasklist

    def get_next_id(self):
        res = self.next_id
        self.next_id += 1
        return res

    def has_file_changed(self):
        return self.file_m != os.path.getmtime(self.file_path)

    def reload(self):
        self.file_m = os.path.getmtime(self.file_path)
        with open(self.file_path, "r", encoding="utf-8") as todotxt_file:
            self.set_text_items(todotxt_file.readlines())

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as todotxt_file:
            for t in self._items:
                todotxt_file.write(t.raw + "\n")
        self.file_m = os.path.getmtime(self.file_path)

    def watch(self, handler):
        path = self.file_path

        class Watcher(watchdog.events.FileSystemEventHandler):
            def on_modified(self, event):
                if (not event.is_directory and
                        os.path.realpath(event.src_path) == os.path.realpath(path)):
                    handler()

        self.observer = watchdog.observers.Observer()
        self.observer.schedule(Watcher(), os.path.dirname(path))
        self.observer.start()

    def stop_watch(self):
        self.observer.stop()
        self.observer.join()
        self.observer = None

    def archive_tasks(self, filter):
        with open(self.archive_path, "a", encoding="utf-8") as donetxt_file:
            for t in filter(self._items):
                donetxt_file.write(t.raw + "\n")
                self._items.remove(t)
        self.save()

    def undo_archive(self):
        with open(self.archive_path, "r+b") as file:

            file.seek(0, os.SEEK_END)
            pos = file.tell()

            buf = b''
            while pos > 0:
                pos -= 1
                file.seek(pos, os.SEEK_SET)
                c = file.read(1)
                if c == b'\n':
                    if buf.strip() != b'':
                        pos += 1
                        break
                    else:
                        buf = b''
                else:
                    buf = c + buf

            res = None
            text = buf.decode('utf-8').strip()
            if text != "":
                res = self.insert_new(-1, text)
                self.save()

            file.seek(pos, os.SEEK_SET)
            file.truncate()
            return res

    def set_text_items(self, text_items):
        self._items = [
            Task(task, self.get_next_id())
            for task in text_items if task.strip() != ""
        ]

    def get_index(self, task_id):
        for i in range(len(self._items)):
            if self._items[i].task_id == task_id:
                return i

    def insert_new(self, index, raw):
        task = Task(raw, self.get_next_id())
        if index == -1: index = len(self._items)
        self._items.insert(index, task)
        return task

    def delete_by_id(self, task_id):
        index = self.get_index(task_id)
        if index is not None:
            del self._items[index]

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
        return sorted(set([context for task in self._items for context in task.contexts]))

    def all_projects(self):
        return sorted(set([project for task in self._items for project in task.projects]))

    def get_items(self):
        return self._items

    def get_items_sorted(self, sort_by):

        def due_prio(task):
            res = task.due_date
            if not res: res = "9999"
            res += task.raw
            if not res: res = "z"
            if task.is_done() or task.is_deleted(): res = "z" + res
            return res

        def prio(task):
            if task.is_done() or task.is_deleted(): return "z" + task.raw
            else: return task.raw

        if sort_by == "due": return sorted(self._items, key=due_prio)
        elif sort_by == "prio": return sorted(self._items, key=prio)

    @staticmethod
    def filter_due(items, date):
        return [t for t in items if t.is_due(date)] if items else []

    @staticmethod
    def filter_by_days(items, days):
        if days >= 0:
            due = Util.get_today_str(days)
            return [item for item in items if item.is_due(due) or not item.has_due()]
        else:
            return items

    @staticmethod
    def filter_pending(items):
        return [t for t in items if not t.is_done()] if items else []

    @staticmethod
    def filter_done_or_del(items):
        return [t for t in items if t.is_done() or t.is_deleted()] if items else []

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
