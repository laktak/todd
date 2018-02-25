import urwid
from tasklib import Tasklist, Util
from urwid_viedit import ViEdit


class TaskItem(urwid.Button):

    def __init__(self, task, key_bindings, colorscheme, parent_ui, wrapping="clip", search=None):
        super(TaskItem, self).__init__("")
        self.task = task  # type Task
        self.key_bindings = key_bindings
        self.wrapping = wrapping
        self.colorscheme = colorscheme
        self.parent_ui = parent_ui
        self.editing = False
        self.update_task(search)

    def selectable(self):
        return True

    def update_task(self, search=None):
        if search:
            show = Tasklist.get_search_highlight(search, self.task.raw)
            text = urwid.Text(show, wrap=self.wrapping)
        else:
            t = self.task
            today = Util.get_today()
            status = t.get_status(today.isoformat())
            status_col = "status_" + status
            if t.is_done(): text_col = status_col
            elif t.priority and t.priority.lower() in "abcdef": text_col = "priority_" + t.priority.lower()
            else: text_col = "plain"

            due_name = Util.get_date_name(t.get_due(), today=today)
            if t.rec_int:
                if t.rec_int[0] == "+": rec_text = "every " + t.rec_int[1:]
                else: rec_text = "after " + t.rec_int
            else: rec_text = ""

            main = urwid.Text((text_col, t.get_desc()), wrap=self.wrapping)
            due = urwid.Text((status_col, due_name))
            rec = urwid.Text(("plain", rec_text))
            context = urwid.Text(("context", ",".join(t.contexts)))
            text = urwid.Columns([
                ("weight", 10, main),
                (12, due),
                (12, rec),
                (15, context),
            ], dividechars=2)

        self._w = urwid.AttrMap(urwid.AttrMap(
            text,
            None, "selected"),
            None, self.colorscheme.focus_map)

    def edit_item(self):
        self.editing = True
        self.edit_widget = ViEdit(caption="", edit_text=self.task.raw, completion_cb=self.completions)
        self._w = urwid.AttrMap(self.edit_widget, "plain_selected")

    def completions(self, text, completion_data={}):
        space = text.rfind(" ")
        start = text[space + 1:]
        words = self.parent_ui.tasklist.all_contexts() + self.parent_ui.tasklist.all_projects()
        try:
            start_idx = words.index(completion_data["last_word"]) + 1
            if start_idx == len(words):
                start_idx = 0
        except (KeyError, ValueError):
            start_idx = 0
        for idx in list(range(start_idx, len(words))) + list(range(0, start_idx)):
            if words[idx].lower().startswith(start.lower()):
                completion_data["last_word"] = words[idx]
                return text[:space + 1] + words[idx] + (": " if space < 0 else "")
        return text

    def end_edit(self):
        self.editing = False
        self.task.update(self._w.original_widget.edit_text.strip())
        self.update_task()
        self.parent_ui.task_changed()

    def keypress(self, size, key):
        if self.editing:
            if key in ["down", "up"]: return None  # don't pass up or down to the ListBox
            elif key == "enter":
                self.end_edit()
                return None
            else:
                return self._w.keypress(size, key)
        else:
            return key
