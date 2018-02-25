import os
import urwid
import collections
from tasklib import Tasklist, Util
import taskui


class MainUI:

    def __init__(self, tasklist, key_bindings, colorscheme):
        self.wrapping = collections.deque(["clip", "space"])
        self.sort_order = collections.deque(["Due", "Prio"])

        self.tasklist = tasklist
        self.items = None
        self.key_bindings = key_bindings

        self.colorscheme = colorscheme
        self.palette = [(key, "", "", "", value["fg"], value["bg"]) for key, value in self.colorscheme.colors.items()]

        self.context_panel = None
        self.active_context = None

        self.search_highlight = False
        self.search_string = ""

        self.listbox = taskui.ViListBox(self.key_bindings, urwid.SimpleListWalker([]))
        urwid.connect_signal(self.listbox.body, "modified", self.task_list_updated)
        self.frame = urwid.Frame(urwid.AttrMap(self.listbox, "plain"), header=None, footer=None)
        self.view = taskui.ViColumns(self.key_bindings, [("weight", 5, self.frame)])
        self.help_panel = None

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke, handle_mouse=False)
        self.loop.screen.set_terminal_properties(colors=256)
        # also see self.loop.widget

    def update_header(self, message=""):
        today = Util.get_today_str()
        self.frame.header = urwid.AttrMap(
            urwid.Columns([
                urwid.Text([
                    ("header_task_count", "{0} Tasks ".format(len(Tasklist.filter_pending(self.items)))),
                    ("header_task_due_count", " {0} due ".format(len(Tasklist.filter_due(self.items, today)))),
                    ("header_sort", " s:{0} ".format(self.sort_order[0])),
                ]),
                # urwid.Text(("header_file", "{0}  {1} ".format(message, self.tasklist.file_path)), align="right"),
                urwid.Text(("header_file", message), align="right"),
            ]), "header")

    def toggle_help_panel(self):
        if self.context_panel: self.toggle_context_panel()
        if self.help_panel:
            self.help_panel = None
            self.loop.widget = self.view
        else:
            self.help_panel = taskui.MainHelp.create_help_panel(self.key_bindings)
            self.loop.widget = urwid.Overlay(self.help_panel, self.view, "center", 70, "middle", ("relative", 90))

    def toggle_sort_order(self):
        self.sort_order.rotate(1)
        self.fill_listbox()
        self.listbox.move_top()

    def toggle_context_panel(self):
        def create_context_panel():
            allc = self.tasklist.all_contexts()

            self.context_list = taskui.ViListBox(self.key_bindings, urwid.SimpleListWalker(
                [urwid.Divider()] +
                [urwid.Text("Switch Context")] +
                [urwid.Divider(u"─")] +
                [urwid.AttrMap(taskui.MenuItem("(all)", self.toggle_context_panel), "dialog_color", "plain_selected")] +
                [urwid.AttrMap(taskui.MenuItem([c[1:]], self.toggle_context_panel), "dialog_color", "plain_selected") for c in allc]
            ))

            if self.active_context:
                for idx, c in enumerate(allc):
                    if c == self.active_context:
                        self.context_list.body.set_focus(idx + 4)
            urwid.connect_signal(self.context_list.body, "modified", self.context_list_updated)
            return urwid.AttrMap(urwid.Padding(self.context_list, left=1, right=1, min_width=10), "dialog_color")

        if self.context_panel:
            self.view.contents.pop()
            self.context_panel = None
        else:
            self.context_panel = create_context_panel()
            self.view.contents.append((self.context_panel, self.view.options(width_type="weight", width_amount=1)))
            self.view.focus_position = 1

    def toggle_wrapping(self, checkbox=None, state=None):
        self.wrapping.rotate(1)
        for item in self.listbox.body:
            item.wrapping = self.wrapping[0]
            item.update_task()

    def update_footer(self, name):
        if name == "edit-help":
            self.frame.footer = urwid.AttrMap(urwid.Pile([
                urwid.Text("Task format: DESCRIPTION +TAG(s) @CONTEXT KEY:VALUE (like +shop @home due:mon or due:2020-10-01)"),
            ]), "footer")
        elif name == "search":
            search_box = taskui.EntryWidget(self.search_string, self.commit_search)
            self.frame.footer = urwid.AttrMap(urwid.Columns([
                (1, urwid.Text("/")),
                search_box,
            ]), "footer")
            urwid.connect_signal(search_box, "change", self.search_updated)
            self.frame.set_focus("footer")
        elif name == "due" or name == "due-":
            edit_box = taskui.EntryWidget("" if name == "due" else "-", self.commit_due)
            self.frame.footer = urwid.AttrMap(urwid.Pile([
                urwid.Columns([(17, urwid.Text("adjust due date:")), edit_box]),
                urwid.Text((
                    "plain",
                    "Add/subtract days, months and years like 7d, -2m or 5y. Also accepts mo, tu, .. su or to(morrow).")),
            ]), "footer")
            self.frame.set_focus("footer")
        else:
            self.frame.footer = None

    def select_by_id(self, task_id):
        for i in range(len(self.listbox.body)):
            if self.listbox.body[i].task.task_id == task_id:
                self.listbox.set_focus(i)
                return
        self.listbox.move_top()

    def save_tasklist(self):
        self.tasklist.save()
        self.update_header("Saved")

    def archive_done(self):
        self.tasklist.archive_done()
        self.fill_listbox()
        self.listbox.move_top()

    def archive_undo(self):
        t = self.tasklist.undo_archive()
        self.fill_listbox()
        self.select_by_id(t.task_id)

    def reload_tasklist_from_file(self):
        self.tasklist.reload()
        self.fill_listbox()
        self.update_header("Reloaded")

    # called by watcher
    def file_updated(self, dummy):
        if self.tasklist.has_file_changed():
            self.reload_tasklist_from_file()

    def task_list_updated(self):
        self.update_header()

    def adjust_priority(self, focus, mod):
        assert mod in [1, -1]
        priorities = ["A", "B", "C", "D", "E", "F", ""]
        lp = len(priorities)
        new_prio = (priorities.index(focus.task.priority) + lp + mod) % lp
        focus.task.set_priority(priorities[new_prio])
        focus.update_task()

    def change_due(self, focus, add=True):
        self.update_footer("due" if add else "due-")

    def commit_due(self, text):
        self.frame.set_focus("body")
        self.update_footer("")
        focus, _ = self.listbox.get_focus()
        try:
            due = focus.task.get_due() or Util.get_today()
            due = Util.mod_date_by(due, text)
            focus.task.set_due(due)
            self.tasklist.save()
            self.fill_listbox()
        except Exception:
            self.update_header("Invalid format!")

    def add_new_task(self):
        task = self.tasklist.append_text("")
        task.set_creation_date(Util.get_today())
        t = taskui.TaskItem(task, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0])
        self.listbox.body.insert(0, t)
        self.listbox.move_top()
        self.edit_task()

    def edit_task(self):
        self.update_footer("edit-help")
        focus, _ = self.listbox.get_focus()
        focus.edit_item()

    def task_changed(self):
        # finished editing
        focus, _ = self.listbox.get_focus()
        focus.task.update_relative_due_date()
        self.update_footer("")
        self.tasklist.save()
        self.fill_listbox()

    def toggle_done(self, focus):
        t = focus.task
        if t.is_done():
            t.set_done(False)
            self.tasklist.save()
        else:
            last = t.raw
            rec = t.set_done()
            if rec:
                self.tasklist.append_text(t.raw)
                t.update(last)
                t.set_due(rec)
                t.set_creation_date(Util.get_today())
            else:
                self.listbox.move_offs(1)
            self.tasklist.archive_done()  # saves

        self.fill_listbox()

    def delete_task(self, focus):
        if self.tasklist.get_items():
            self.listbox.move_offs(1)
            self.tasklist.delete_by_id(focus.task.task_id)
            self.tasklist.save()
            self.fill_listbox()

    def start_search(self):
        self.update_footer("search")

    def search_updated(self, edit_item, search_string):
        self.search_string = search_string
        if search_string:
            self.search_highlight = True
            self.fill_listbox()

    def commit_search(self, text):
        self.frame.set_focus("body")
        self.search_highlight = False
        if not Tasklist.prep_search(self.search_string):
            self.search_string = ""
            self.update_footer("")
        self.fill_listbox()

    def clear_search_term(self):
        if self.search_string:
            self.search_string = ""
            self.update_footer("")
            self.fill_listbox()

    def context_list_updated(self):
        focus = self.context_list.get_focus()[0].original_widget.text
        if focus == "(all)":
            self.active_context = None
            self.fill_listbox()
        else:
            self.active_context = "@" + focus
            self.fill_listbox()

    def fill_listbox(self):
        # clear
        focus, _ = self.listbox.get_focus()
        last_id = focus.task.task_id if focus else -1

        sort_by = self.sort_order[0]
        items = self.tasklist.get_items_sorted(sort_by.lower())

        if self.active_context:
            items = Tasklist.filter_context(items, self.active_context)

        search = None
        if self.search_string != "":
            search = Tasklist.prep_search(self.search_string)
            items = Tasklist.search(search, items)
            if not self.search_highlight: search = None

        self.items = items
        self.listbox.body.clear()
        self.listbox.body.extend(
            [taskui.TaskItem(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0], search=search) for t in items])

        self.select_by_id(last_id)
        self.update_header()

    def keystroke(self, key):

        if self.help_panel:
            if self.key_bindings.is_bound_to(key, "quit") or \
                self.key_bindings.is_bound_to(key, "toggle-help"): self.toggle_help_panel()
            return

        focus, _ = self.listbox.get_focus()

        if self.key_bindings.is_bound_to(key, "quit"): raise urwid.ExitMainLoop()

        # View options
        elif self.key_bindings.is_bound_to(key, "toggle-help"): self.toggle_help_panel()
        elif self.key_bindings.is_bound_to(key, "switch-context"): self.toggle_context_panel()
        elif self.key_bindings.is_bound_to(key, "toggle-wrapping"): self.toggle_wrapping()
        elif self.key_bindings.is_bound_to(key, "toggle-sort-order"): self.toggle_sort_order()
        elif self.key_bindings.is_bound_to(key, "search"): self.start_search()
        elif self.key_bindings.is_bound_to(key, "search-clear"): self.clear_search_term()

        # Editing
        elif self.key_bindings.is_bound_to(key, "new"): self.add_new_task()
        elif self.key_bindings.is_bound_to(key, "edit"): self.edit_task()
        elif self.key_bindings.is_bound_to(key, "toggle-done"): self.toggle_done(focus)
        elif self.key_bindings.is_bound_to(key, "delete"): self.delete_task(focus)
        elif self.key_bindings.is_bound_to(key, "priority-higher"): self.adjust_priority(focus, 1)
        elif self.key_bindings.is_bound_to(key, "priority-lower"): self.adjust_priority(focus, -1)
        elif self.key_bindings.is_bound_to(key, "add-due"): self.change_due(focus, True)
        elif self.key_bindings.is_bound_to(key, "subtract-due"): self.change_due(focus, False)

        elif self.key_bindings.is_bound_to(key, "archive"): self.archive_done()
        elif self.key_bindings.is_bound_to(key, "undo-archive"): self.archive_undo()
        elif self.key_bindings.is_bound_to(key, "save"): self.save_tasklist()
        elif self.key_bindings.is_bound_to(key, "reload"): self.reload_tasklist_from_file()

    def main(self, enable_word_wrap=False):

        if enable_word_wrap:
            self.toggle_wrapping()

        self.fill_listbox()

        pipe = self.loop.watch_pipe(self.file_updated)

        def piper():
            os.write(pipe, b'updated')  # trigger file_updated

        self.tasklist.watch(piper)
        self.loop.run()
        self.tasklist.stop_watch()
