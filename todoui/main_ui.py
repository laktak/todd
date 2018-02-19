import urwid
import collections
from todolib.todo import Todo, Util
from todolib.todos import Todos
from todoui.todoitem import TodoItem
from todoui.components import EntryWidget, MenuItem, ViColumns, ViListBox
from todoui.main_help import MainHelp

class MainUI:

    def __init__(self, todos, key_bindings, colorscheme):
        self.wrapping = collections.deque(['clip', 'space'])
        self.sort_order = collections.deque(["Due", "Prio"])

        self.todos = todos
        self.items = None
        self.key_bindings = key_bindings

        self.colorscheme = colorscheme
        self.palette = [(key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items()]

        self.context_panel = None
        self.active_context = None

        self.searching = False
        self.search_string = ''

        self.header = self.create_header()
        self.listbox = ViListBox(self.key_bindings, urwid.SimpleListWalker([]))
        self.frame = urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=None)
        self.view = ViColumns(self.key_bindings, [('weight', 2, self.frame)])
        self.help_panel = None

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.screen.set_terminal_properties(colors=256)
        # also see self.loop.widget

    def create_header(self, message=""):
        today = Todo.get_current_date()
        return urwid.AttrMap(
            urwid.Columns([
                urwid.Text([
                    ('header_todo_count', "{0} Todos ".format(len(Todos.filter_pending(self.items)))),
                    ('header_todo_due_count', " {0} due ".format(len(Todos.filter_due(self.items, today)))),
                    ('header_sort', " s:{0} ".format(self.sort_order[0])),
                ]),
                urwid.Text(('header_file', "{0}  {1} ".format(message, self.todos.file_path)), align='right')
            ]), 'header')

    def create_context_panel(self):
        allc = self.todos.all_contexts()

        self.context_list = ViListBox(self.key_bindings, urwid.SimpleListWalker(
            [urwid.Text('Switch Context', align='center')] +
            [urwid.Divider(u'─')] +
            [urwid.AttrMap(MenuItem('(all)', self.toggle_context_panel), 'dialog_color', 'plain_selected')] +
            [urwid.AttrMap(MenuItem([c[1:]], self.toggle_context_panel), 'dialog_color', 'plain_selected') for c in allc]
        ))

        if self.active_context:
            for idx, c in enumerate(allc):
                if c == self.active_context:
                    self.context_list.body.set_focus(idx + 3)
        urwid.connect_signal(self.context_list.body, 'modified', self.context_list_updated)
        return urwid.AttrMap(urwid.Padding(self.context_list, left=1, right=1, min_width=10), 'dialog_color')

    def toggle_help_panel(self, button=None):
        if self.context_panel: self.toggle_context_panel()
        if self.help_panel:
            self.help_panel = None
            self.loop.widget = self.view
        else:
            self.help_panel = MainHelp.create_help_panel(self.key_bindings)
            self.loop.widget = urwid.Overlay(self.help_panel, self.view, 'center', 70, 'middle', ('relative', 90))

    def toggle_sort_order(self, button=None):
        self.sort_order.rotate(1)
        self.fill_listbox()
        self.set_selection_top()

    def toggle_context_panel(self, button=None):
        if self.context_panel:
            self.view.contents.pop()
            self.context_panel = None
        else:
            self.context_panel = self.create_context_panel()
            self.view.contents.append((self.context_panel, self.view.options(width_type='weight', width_amount=1)))
            self.view.focus_position = 1

    def toggle_wrapping(self, checkbox=None, state=None):
        self.wrapping.rotate(1)
        for item in self.listbox.body:
            item.wrapping = self.wrapping[0]
            item.update_todo()

    def update_header(self, message=""):
        self.frame.header = self.create_header(message)

    def update_footer(self, name=None, set_focus=False):
        if name == "search":
            self.search_box = EntryWidget(self.search_string, self.finalize_search)
            self.frame.footer = urwid.AttrMap(urwid.Columns([
                (1, urwid.Text('/')),
                self.search_box,
                (16, urwid.AttrMap(
                    urwid.Button([('header_file', 'C'), 'lear Search'], on_press=self.clear_search_term),
                    'header', 'plain_selected'))
            ]), 'footer')
            urwid.connect_signal(self.search_box, 'change', self.search_box_updated)
        elif name == "due" or name == "due-":
            self.edit_box = EntryWidget("" if name == "due" else "-", self.finalize_due)
            self.frame.footer = urwid.AttrMap(urwid.Columns([
                (12, urwid.Text('adjust due:')),
                self.edit_box,
            ]), 'footer')
        else:
            self.frame.footer = None

        if set_focus:
            if self.frame.footer: self.frame.set_focus('footer')
            else: self.frame.set_focus('body')

    def visible_lines(self):
        lines = self.loop.screen_size[1] - 1  # minus one for the header
        if self.searching:
            lines -= 1
        return lines

    def set_selection_raw(self, raw_index):
        for i in range(len(self.listbox.body) - 1):
            if self.listbox.body[i].todo.raw_index == raw_index:
                self.listbox.set_focus(i)
                return
        self.set_selection_top()

    def listbox_count(self):
        return len(self.listbox.body)
    def set_selection_top(self):
        if self.listbox_count():
            self.listbox.set_focus(0)

    def set_selection_bottom(self):
        if self.listbox_count():
            self.listbox.set_focus(self.listbox_count() - 1)

    def move_selection_down(self):
        self.listbox.keypress((0, self.visible_lines()), 'down')

    def move_selection_up(self):
        self.listbox.keypress((0, self.visible_lines()), 'up')

    def save_todos(self, button=None):
        self.todos.save()
        self.update_header("Saved")

    def archive_done_todos(self):
        if self.todos.archive_done():
            self.fill_listbox()
            self.set_selection_top()

    def reload_todos_from_file(self, button=None):
        self.todos.reload_from_file()
        self.fill_listbox()
        self.update_header("Reloaded")


    def adjust_priority(self, focus, higher=True):
        priorities = ['', 'A', 'B', 'C', 'D', 'E', 'F']
        if higher:
            new_priority = priorities.index(focus.todo.priority) - 1
        else:
            new_priority = priorities.index(focus.todo.priority) + 1

        if new_priority < 0:
            focus.todo.change_priority(priorities[len(priorities) - 1])
        elif new_priority < len(priorities):
            focus.todo.change_priority(priorities[new_priority])
        else:
            focus.todo.change_priority(priorities[0])

        focus.update_todo()

    def change_due(self, focus, add=True):
        self.update_footer("due" if add else "due-", set_focus=True)

    def finalize_due(self, text):
        self.frame.set_focus('body')
        self.update_footer()
        focus, focus_index = self.listbox.get_focus()
        due = Util.date_add_interval_str(focus.todo.due, text)
        focus.todo.set_due(due)
        focus.update_todo()

    def add_new_todo(self):
        new_index = self.todos.append('', add_creation_date=False)
        self.listbox.body.insert(0, TodoItem(self.todos[new_index], self.key_bindings, self.colorscheme, self, editing=True, wrapping=self.wrapping[0]))
        self.set_selection_top()

    def todo_changed(self):
        # finished editing
        self.fill_listbox()

    def toggle_done(self, focus):
        t = focus.todo
        if t.is_done():
            t.set_done(False)
        else:
            self.todos.archive_done()
            rec = t.set_done()
            if rec:
                new_index = self.todos.append(t.raw, add_creation_date=False)
                t.set_done(False)
                t.set_due(rec)
            else:
                self.move_selection_down()
        self.fill_listbox()

    def delete_todo(self, focus):
        if self.todos.todo_items:
            self.move_selection_down()
            self.todos.delete(focus.todo.raw_index)
            self.fill_listbox()

    def start_search(self):
        self.searching = True
        self.update_footer("search", set_focus=True)

    def search_box_updated(self, edit_item, search_string):
        self.search_string = search_string
        if search_string:
            self.searching = True
            self.fill_listbox()

    def finalize_search(self, text):
        self.search_string = ''
        self.frame.set_focus('body')
        for item in self.listbox.body:
            item.update_todo()

    def clear_search_term(self, button=None):
        self.searching = False
        self.search_string = ''
        self.update_footer()
        self.fill_listbox()


    def context_list_updated(self):
        focus = self.context_list.get_focus()[0].original_widget.text
        if focus == '(all)':
            self.active_context = None
            self.fill_listbox()
        else:
            self.active_context = '@' + focus
            self.fill_listbox()

    def fill_listbox(self):
        # clear
        focus, focus_index = self.listbox.get_focus()
        last_idx = focus.todo.raw_index if focus else -1

        sort_by = self.sort_order[0]
        items = self.todos.get_items_sorted(sort_by.lower())

        if self.active_context:
            items = Todos.filter_context(items, self.active_context)

        if self.searching:
            items = Todos.search(items, self.search_string)

        self.items = items
        self.listbox.body.clear()
        self.listbox.body.extend([TodoItem(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0]) for t in items])

        self.set_selection_raw(last_idx)
        self.update_header()


    def keystroke(self, input):

        if self.help_panel:
            if self.key_bindings.is_binded_to(input, 'quit') or \
                self.key_bindings.is_binded_to(input, 'toggle-help'): self.toggle_help_panel()
            return

        focus, focus_index = self.listbox.get_focus()

        if self.key_bindings.is_binded_to(input, 'quit'): raise urwid.ExitMainLoop()

        # Movement
        elif self.key_bindings.is_binded_to(input, 'top'): self.set_selection_top()
        elif self.key_bindings.is_binded_to(input, 'bottom'): self.set_selection_bottom()

        # View options
        elif self.key_bindings.is_binded_to(input, 'toggle-help'): self.toggle_help_panel()
        elif self.key_bindings.is_binded_to(input, 'toggle-context'): self.toggle_context_panel()
        elif self.key_bindings.is_binded_to(input, 'toggle-wrapping'): self.toggle_wrapping()
        elif self.key_bindings.is_binded_to(input, 'toggle-sort-order'): self.toggle_sort_order()
        elif self.key_bindings.is_binded_to(input, 'search'): self.start_search()
        elif self.key_bindings.is_binded_to(input, 'search-clear'):
            if self.searching: self.clear_search_term()

        # Editing
        elif self.key_bindings.is_binded_to(input, 'toggle-done'): self.toggle_done(focus)
        elif self.key_bindings.is_binded_to(input, 'archive'): self.archive_done_todos()
        elif self.key_bindings.is_binded_to(input, 'delete'): self.delete_todo(focus)
        elif self.key_bindings.is_binded_to(input, 'new'): self.add_new_todo()
        elif self.key_bindings.is_binded_to(input, 'priority-higher'): self.adjust_priority(focus, higher=True)
        elif self.key_bindings.is_binded_to(input, 'priority-lower'): self.adjust_priority(focus, higher=False)
        elif self.key_bindings.is_binded_to(input, 'add-due'): self.change_due(focus, True)
        elif self.key_bindings.is_binded_to(input, 'subtract-due'): self.change_due(focus, False)

        elif self.key_bindings.is_binded_to(input, 'save'): self.save_todos()
        elif self.key_bindings.is_binded_to(input, 'reload'): self.reload_todos_from_file()


    def main(self, enable_word_wrap=False):


        if enable_word_wrap:
            self.toggle_wrapping()

        self.fill_listbox()

        self.loop.run()
