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
        self.sorting = collections.deque(["Unsorted", "Descending", "Ascending"])
        self.sorting_display = {"Unsorted": "-", "Descending": "v", "Ascending": "^"}

        self.todos = todos
        self.items = None
        self.key_bindings = key_bindings

        self.colorscheme = colorscheme
        self.palette = [(key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items()]

        self.active_projects = []
        self.active_contexts = []

        self.help_panel_is_open = False
        self.context_panel = None
        self.filter_panel_is_open = False
        self.filtering = False
        self.searching = False
        self.search_string = ''
        self.yanked_text = ''

    def create_header(self, message=""):
        today = Todo.get_current_date()
        return urwid.AttrMap(
            urwid.Columns([
                urwid.Text([
                    ('header_todo_count', "{0} Todos ".format(len(Todos.filter_pending(self.items)))),
                    ('header_todo_due_count', " {0} due ".format(len(Todos.filter_due(self.items, today)))),
                    # ('header_todo_done_count', " {0} Done ".format(len(Todos.filter_done(self.items)))),
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

        if self.active_contexts:
            sel = self.active_contexts[0]
            for idx, c in enumerate(allc):
                if c == sel:
                    self.context_list.body.set_focus(idx + 3)
        urwid.connect_signal(self.context_list.body, 'modified', self.context_list_updated)
        return urwid.AttrMap(urwid.Padding(self.context_list, left=1, right=1, min_width=10), 'dialog_color')

    def create_filter_panel(self):
        flist = ViListBox(self. key_bindings,
            [urwid.Text('Contexts & Projects', align='center')] +
            [urwid.Divider(u'─')] +
            [urwid.AttrWrap(urwid.CheckBox(c, state=(c in self.active_contexts), on_state_change=self.checkbox_clicked, user_data=['context', c]), 'context_dialog_color', 'context_selected') for c in self.todos.all_contexts()] +
            [urwid.Divider(u'─')] +
            [urwid.AttrWrap(urwid.CheckBox(p, state=(p in self.active_projects), on_state_change=self.checkbox_clicked, user_data=['project', p]), 'project_dialog_color', 'project_selected') for p in self.todos.all_projects()] +
            [urwid.Divider(u'─')] +
            [urwid.AttrMap(urwid.Button(['Clear ', ('header_file_dialog_color', 'F'), 'ilters'], on_press=self.clear_filters), 'dialog_color', 'plain_selected')]
        )
        return urwid.AttrMap(urwid.Padding(flist, left=1, right=1, min_width=10), 'dialog_color')

    def toggle_help_panel(self, button=None):
        if self.context_panel: self.toggle_context_panel()
        if self.filter_panel_is_open: self.toggle_filter_panel()
        if self.help_panel_is_open:
            self.view.contents.pop()
            self.help_panel_is_open = False
        else:
            self.help_panel = MainHelp.create_help_panel(self.key_bindings)
            self.view.contents.append((self.help_panel, self.view.options(width_type='weight', width_amount=2)))
            self.view.set_focus(1)
            self.help_panel_is_open = True

    def toggle_sorting(self, button=None):
        self.sorting.rotate(1)
        # if self.sorting[0] == 'Ascending':
        # elif self.sorting[0] == 'Descending':
        # elif self.sorting[0] == 'Unsorted':
        self.fill_listbox()
        self.set_selection_top()

    def toggle_context_panel(self, button=None):
        if self.help_panel_is_open: self.toggle_help_panel()
        if self.filter_panel_is_open: self.toggle_filter_panel()
        if self.context_panel:
            self.view.contents.pop()
            self.context_panel = None
        else:
            self.context_panel = self.create_context_panel()
            self.view.contents.append((self.context_panel, self.view.options(width_type='weight', width_amount=1)))
            self.view.focus_position = 1

    def toggle_filter_panel(self, button=None):
        if self.help_panel_is_open: self.toggle_help_panel()
        if self.context_panel: self.toggle_context_panel()
        if self.filter_panel_is_open:
            self.view.contents.pop()
            self.filter_panel_is_open = False
        else:
            self.filter_panel = self.create_filter_panel()
            self.view.contents.append((self.filter_panel, self.view.options(width_type='weight', width_amount=1)))
            self.filter_panel_is_open = True

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
            self.active_contexts = []
            self.filtering = False
            self.fill_listbox()
        else:
            self.active_contexts = [ '@' + focus ]
            self.active_projects = []
            self.filter_todo_list()

    def fill_listbox(self):
        # clear
        focus, focus_index = self.listbox.get_focus()
        last_idx = focus.todo.raw_index if focus else -1

        for i in range(len(self.listbox.body) - 1, -1, -1):
            self.listbox.body.pop(i)

        items = self.todos.get_items_sorted()

        if self.filtering:
            items = Todos.filter_contexts_and_projects(items, self.active_contexts, self.active_projects)

        if self.searching:
            items = Todos.search(items, self.search_string)

        self.items = items
        for t in items:
            self.listbox.body.append(TodoItem(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0]))

        self.set_selection_raw(last_idx)
        self.update_header()

    def filter_todo_list(self):
        self.filtering = True
        self.fill_listbox()

    def clear_filters(self, button=None):
        self.active_projects = []
        self.active_contexts = []
        self.filtering = False
        self.view.set_focus(0)
        self.update_filters()
        self.fill_listbox()

    def checkbox_clicked(self, checkbox, state, data):
        if state:
            if data[0] == 'context':
                self.active_contexts.append(data[1])
            else:
                self.active_projects.append(data[1])
        else:
            if data[0] == 'context':
                self.active_contexts.remove(data[1])
            else:
                self.active_projects.remove(data[1])

        if self.active_projects or self.active_contexts:
            self.filter_todo_list()
            self.view.set_focus(0)
        else:
            self.clear_filters()

    def update_filters(self, new_contexts=[], new_projects=[]):
        if self.active_contexts:
            for c in new_contexts:
                self.active_contexts.append(c)
        if self.active_projects:
            for p in new_projects:
                self.active_projects.append(p)
        self.update_filter_panel()

    def update_filter_panel(self):
        self.filter_panel = self.create_filter_panel()
        if len(self.view.widget_list) > 1:
            self.view.widget_list.pop()
            self.view.widget_list.append(self.filter_panel)

    def keystroke(self, input):
        focus, focus_index = self.listbox.get_focus()

        if self.key_bindings.is_binded_to(input, 'quit'): raise urwid.ExitMainLoop()

        # Movement
        elif self.key_bindings.is_binded_to(input, 'top'): self.set_selection_top()
        elif self.key_bindings.is_binded_to(input, 'bottom'): self.set_selection_bottom()

        # View options
        elif self.key_bindings.is_binded_to(input, 'toggle-help'): self.toggle_help_panel()
        elif self.key_bindings.is_binded_to(input, 'toggle-context'): self.toggle_context_panel()
        elif self.key_bindings.is_binded_to(input, 'toggle-filter'): self.toggle_filter_panel()
        elif self.key_bindings.is_binded_to(input, 'clear-filter'): self.clear_filters()
        elif self.key_bindings.is_binded_to(input, 'toggle-wrapping'): self.toggle_wrapping()
        elif self.key_bindings.is_binded_to(input, 'toggle-sorting'): self.toggle_sorting()
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

        self.header = self.create_header()

        self.listbox = ViListBox(self.key_bindings, urwid.SimpleListWalker([]))

        self.frame = urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=None)

        self.view = ViColumns(self.key_bindings, [('weight', 2, self.frame)])

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.screen.set_terminal_properties(colors=256)

        if enable_word_wrap:
            self.toggle_wrapping()

        self.fill_listbox()

        self.loop.run()
