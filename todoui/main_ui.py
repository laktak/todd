import urwid
import collections
from todolib.todo import Todo, Util
from todoui.advanced_edit import AdvancedEdit
from todoui.components_ui import EntryWidget, MenuItem, TodoWidget, ViColumns, ViListBox
from todoui.main_help import MainHelp

class MainUI:

    def __init__(self, todos, key_bindings, colorscheme):
        self.wrapping = collections.deque(['clip', 'space'])
        self.border = collections.deque(['no border', 'bordered'])
        self.sorting = collections.deque(["Unsorted", "Descending", "Ascending"])
        self.sorting_display = {"Unsorted": "-", "Descending": "v", "Ascending": "^"}

        self.todos = todos
        self.key_bindings = key_bindings

        self.colorscheme = colorscheme
        self.palette = [(key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items()]

        self.active_projects = []
        self.active_contexts = []

        self.toolbar_is_open = False
        self.help_panel_is_open = False
        self.context_panel = None
        self.filter_panel_is_open = False
        self.filtering = False
        self.searching = False
        self.search_string = ''
        self.yanked_text = ''

    def visible_lines(self):
        lines = self.loop.screen_size[1] - 1  # minus one for the header
        if self.toolbar_is_open:
            lines -= 1
        if self.searching:
            lines -= 1
        return lines

    def move_selection_down(self):
        self.listbox.keypress((0, self.visible_lines()), 'down')

    def move_selection_up(self):
        self.listbox.keypress((0, self.visible_lines()), 'up')

    def move_selection_top(self):
        self.listbox.set_focus(0)

    def move_selection_bottom(self):
        self.listbox.set_focus(len(self.listbox.body) - 1)

    def toggle_help_panel(self, button=None):
        if self.context_panel: self.toggle_context_panel()
        if self.filter_panel_is_open: self.toggle_filter_panel()
        if self.help_panel_is_open:
            self.view.contents.pop()
            self.help_panel_is_open = False
            # set header line to word-wrap contents
            # for header_column in self.frame.header.original_widget.contents:
            #     header_column[0].set_wrap_mode('space')
        else:
            self.help_panel = MainHelp.create_help_panel(self.key_bindings)
            self.view.contents.append((self.help_panel, self.view.options(width_type='weight', width_amount=3)))
            self.view.set_focus(1)
            self.help_panel_is_open = True
            # set header line to clip contents
            # for header_column in self.frame.header.original_widget.contents:
            #     header_column[0].set_wrap_mode('clip')

    def toggle_sorting(self, button=None):
        self.delete_todo_widgets()
        self.sorting.rotate(1)
        if self.sorting[0] == 'Ascending':
            self.todos.sorted()
        elif self.sorting[0] == 'Descending':
            self.todos.sorted_reverse()
        elif self.sorting[0] == 'Unsorted':
            self.todos.sorted_raw()
        self.reload_todos_from_memory()
        self.move_selection_top()
        self.update_header()

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
        for widget in self.listbox.body:
            widget.wrapping = self.wrapping[0]
            widget.update_todo()
        if self.toolbar_is_open:
            self.update_header()

    def toggle_border(self, checkbox=None, state=None):
        self.border.rotate(1)
        for widget in self.listbox.body:
            widget.border = self.border[0]
            widget.update_todo()
        if self.toolbar_is_open:
            self.update_header()

    def toggle_toolbar(self):
        self.toolbar_is_open = not self.toolbar_is_open
        self.update_header()

    def swap_down(self):
        focus, focus_index = self.listbox.get_focus()
        if not self.filtering and not self.searching:
            if focus_index + 1 < len(self.listbox.body):
                self.todos.swap(focus_index, focus_index + 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index + 1].todo = self.todos[focus_index + 1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index + 1].update_todo()
                self.move_selection_down()

    def swap_up(self):
        focus, focus_index = self.listbox.get_focus()
        if not self.filtering and not self.searching:
            if focus_index > 0:
                self.todos.swap(focus_index, focus_index - 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index - 1].todo = self.todos[focus_index - 1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index - 1].update_todo()
                self.move_selection_up()

    def save_todos(self, button=None):
        self.todos.save()
        self.update_header("Saved")

    def archive_done_todos(self):
        if self.todos.archive_done():
            self.delete_todo_widgets()
            self.reload_todos_from_memory()
            self.move_selection_top()
            self.update_header()

    def reload_todos_from_file(self, button=None):
        self.delete_todo_widgets()

        self.todos.reload_from_file()

        for t in self.todos.todo_items:
            self.listbox.body.append(TodoWidget(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]))

        self.update_header("Reloaded")

    def keystroke(self, input):
        focus, focus_index = self.listbox.get_focus()

        if self.key_bindings.is_binded_to(input, 'quit'):
            raise urwid.ExitMainLoop()

        # Movement
        elif self.key_bindings.is_binded_to(input, 'top'):
            self.move_selection_top()
        elif self.key_bindings.is_binded_to(input, 'bottom'):
            self.move_selection_bottom()
        elif self.key_bindings.is_binded_to(input, 'swap-down'):
            self.swap_down()
        elif self.key_bindings.is_binded_to(input, 'swap-up'):
            self.swap_up()
        elif self.key_bindings.is_binded_to(input, 'change-focus'):
            current_focus = self.frame.get_focus()
            if current_focus == 'body':

                if self.filter_panel_is_open and self.toolbar_is_open:

                    if self.view.focus_position == 1:
                        self.view.focus_position = 0
                        self.frame.focus_position = 'header'
                    elif self.view.focus_position == 0:
                        self.view.focus_position = 1

                elif self.toolbar_is_open:
                    self.frame.focus_position = 'header'

                elif self.filter_panel_is_open:
                    if self.view.focus_position == 1:
                        self.view.focus_position = 0
                    elif self.view.focus_position == 0:
                        self.view.focus_position = 1

            elif current_focus == 'header':
                self.frame.focus_position = 'body'

        # View options
        elif self.key_bindings.is_binded_to(input, 'toggle-help'):
            self.toggle_help_panel()
        elif self.key_bindings.is_binded_to(input, 'toggle-toolbar'):
            self.toggle_toolbar()
        elif self.key_bindings.is_binded_to(input, 'toggle-context'):
            self.toggle_context_panel()
        elif self.key_bindings.is_binded_to(input, 'toggle-filter'):
            self.toggle_filter_panel()
        elif self.key_bindings.is_binded_to(input, 'clear-filter'):
            self.clear_filters()
        elif self.key_bindings.is_binded_to(input, 'toggle-wrapping'):
            self.toggle_wrapping()
        elif self.key_bindings.is_binded_to(input, 'toggle-borders'):
            self.toggle_border()
        elif self.key_bindings.is_binded_to(input, 'toggle-sorting'):
            self.toggle_sorting()

        elif self.key_bindings.is_binded_to(input, 'search'):
            self.start_search()
        elif self.key_bindings.is_binded_to(input, 'search-clear'):
            if self.searching:
                self.clear_search_term()

        # Editing
        elif self.key_bindings.is_binded_to(input, 'toggle-complete'):
            t = focus.todo
            if t.is_complete():
                t.incomplete()
            else:
                rec = t.complete()
                if rec:
                    new_index = self.todos.append(t.raw, add_creation_date=False)
                    self.listbox.body.append(TodoWidget(self.todos[new_index], self.key_bindings, self.colorscheme, self, editing=False, wrapping=self.wrapping[0], border=self.border[0]))
                    t.incomplete()
                    t.set_due(rec)
            focus.update_todo()
            self.update_header()

        elif self.key_bindings.is_binded_to(input, 'archive'):
            self.archive_done_todos()

        elif self.key_bindings.is_binded_to(input, 'delete'):
            if self.todos.todo_items:
                i = focus.todo.raw_index
                self.todos.delete(i)
                del self.listbox.body[focus_index]
                self.update_header()

        elif self.key_bindings.is_binded_to(input, 'append'):
            self.add_new_todo(position='append')
        elif self.key_bindings.is_binded_to(input, 'insert-before'):
            self.add_new_todo(position='insert_before')
        elif self.key_bindings.is_binded_to(input, 'insert-after'):
            self.add_new_todo(position='insert_after')

        elif self.key_bindings.is_binded_to(input, 'priority-up'):
            self.adjust_priority(focus, up=True)

        elif self.key_bindings.is_binded_to(input, 'priority-down'):
            self.adjust_priority(focus, up=False)

        elif self.key_bindings.is_binded_to(input, 'add-due'):
            self.change_due(focus, True)
        elif self.key_bindings.is_binded_to(input, 'subtract-due'):
            self.change_due(focus, False)

        # Save current file
        elif self.key_bindings.is_binded_to(input, 'save'):
            self.save_todos()

        # Reload original file
        elif self.key_bindings.is_binded_to(input, 'reload'):
            self.reload_todos_from_file()

    def adjust_priority(self, focus, up=True):
        priorities = ['', 'A', 'B', 'C', 'D', 'E', 'F']
        if up:
            new_priority = priorities.index(focus.todo.priority) + 1
        else:
            new_priority = priorities.index(focus.todo.priority) - 1

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
        due = Util.scan_interval(focus.todo.get_due(), text)
        focus.todo.set_due(due)
        focus.update_todo()

    def add_new_todo(self, position=False):
        if len(self.listbox.body) == 0:
            position = 'append'
        else:
            focus_index = self.listbox.get_focus()[1]

        if self.filtering:
            position = 'append'

        if position is 'append':
            new_index = self.todos.append('', add_creation_date=False)
            self.listbox.body.append(TodoWidget(self.todos[new_index], self.key_bindings, self.colorscheme, self, editing=True, wrapping=self.wrapping[0], border=self.border[0]))
        else:
            if position is 'insert_after':
                new_index = self.todos.insert(focus_index + 1, '', add_creation_date=False)
            elif position is 'insert_before':
                new_index = self.todos.insert(focus_index, '', add_creation_date=False)

            self.listbox.body.insert(new_index, TodoWidget(self.todos[new_index], self.key_bindings, self.colorscheme, self, editing=True, wrapping=self.wrapping[0], border=self.border[0]))

        if position:
            if self.filtering:
                self.listbox.set_focus(len(self.listbox.body) - 1)
            else:
                self.listbox.set_focus(new_index)
            # edit_widget = self.listbox.body[new_index]._w
            # edit_widget.edit_text += ' '
            # edit_widget.set_edit_pos(len(self.todos[new_index].raw) + 1)
            self.update_header()

    def create_header(self, message=""):
        return urwid.AttrMap(
            urwid.Columns([
                urwid.Text([
                    ('header_todo_count', "{0} Todos ".format(self.todos.__len__())),
                    ('header_todo_pending_count', " {0} Pending ".format(self.todos.pending_items_count())),
                    ('header_todo_done_count', " {0} Done ".format(self.todos.done_items_count())),
                ]),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text(('header_file', "{0}  {1} ".format(message, self.todos.file_path)), align='right')
            ]), 'header')

    def create_toolbar(self):
        return urwid.AttrMap(urwid.Columns([
            urwid.Padding(
                urwid.AttrMap(
                    urwid.CheckBox([('header_file', 'w'), 'ord wrap'], state=(self.wrapping[0] == 'space'), on_state_change=self.toggle_wrapping),
                    'header', 'plain_selected'), right=2),

            urwid.Padding(
                urwid.AttrMap(
                    urwid.CheckBox([('header_file', 'b'), 'orders'], state=(self.border[0] == 'bordered'), on_state_change=self.toggle_border),
                    'header', 'plain_selected'), right=2),

            urwid.Padding(
                urwid.AttrMap(
                    urwid.Button([('header_file', 'R'), 'eload'], on_press=self.reload_todos_from_file),
                    'header', 'plain_selected'), right=2),

            urwid.Padding(
                urwid.AttrMap(
                    urwid.Button([('header_file', 'S'), 'ave'], on_press=self.save_todos),
                    'header', 'plain_selected'), right=2),

            urwid.Padding(
                urwid.AttrMap(
                    urwid.Button([('header_file', 's'), 'ort: ' + self.sorting_display[self.sorting[0]]], on_press=self.toggle_sorting),
                    'header', 'plain_selected'), right=2),

            urwid.Padding(
                urwid.AttrMap(
                    urwid.Button([('header_file', 'f'), 'ilter'], on_press=self.toggle_filter_panel),
                    'header', 'plain_selected'), right=2)
        ]), 'header')

    def search_box_updated(self, edit_widget, new_contents):
        self.search_string = new_contents
        self.search_todo_list(self.search_string)

    def search_todo_list(self, search_string=""):
        if search_string:
            self.delete_todo_widgets()

            self.searching = True

            for t in self.todos.search(search_string):
                self.listbox.body.append(TodoWidget(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]))

    def start_search(self):
        self.searching = True
        self.update_footer("search", set_focus=True)

    def finalize_search(self, text):
        self.search_string = ''
        self.frame.set_focus('body')
        for widget in self.listbox.body:
            widget.update_todo()

    def clear_search_term(self, button=None):
        self.delete_todo_widgets()
        self.searching = False
        self.search_string = ''
        self.update_footer()
        self.reload_todos_from_memory()

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

    def context_list_updated(self):
        focus = self.context_list.get_focus()[0].original_widget.text
        if focus == '(all)':
            self.active_contexts = []
            self.delete_todo_widgets()
            self.reload_todos_from_memory()
        else:
            self.active_contexts = [ '@' + focus ]
            self.active_projects = []
            self.filter_todo_list()

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

    def delete_todo_widgets(self):
        for i in range(len(self.listbox.body) - 1, -1, -1):
            self.listbox.body.pop(i)

    def reload_todos_from_memory(self):
        for t in self.todos.todo_items:
            self.listbox.body.append(TodoWidget(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]))

    def clear_filters(self, button=None):
        self.delete_todo_widgets()
        self.reload_todos_from_memory()

        self.active_projects = []
        self.active_contexts = []
        self.filtering = False
        self.view.set_focus(0)
        self.update_filters()

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

    def filter_todo_list(self):
        self.delete_todo_widgets()

        for t in self.todos.filter_contexts_and_projects(self.active_contexts, self.active_projects):
            self.listbox.body.append(TodoWidget(t, self.key_bindings, self.colorscheme, self, wrapping=self.wrapping[0], border=self.border[0]))

        self.filtering = True

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

    def update_header(self, message=""):
        if self.toolbar_is_open:
            self.frame.header = urwid.Pile([self.create_header(message), self.create_toolbar()])
        else:
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

    def main(self,
             enable_borders=False,
             enable_word_wrap=False,
             show_toolbar=False,
             show_filter_panel=False):

        self.header = self.create_header()

        self.listbox = ViListBox(self.key_bindings, urwid.SimpleListWalker(
            [TodoWidget(t, self.key_bindings, self.colorscheme, self) for t in self.todos.todo_items]
        ))

        self.frame = urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=None)

        self.view = ViColumns(self.key_bindings,
                              [
                                  ('weight', 2, self.frame)
                              ])

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.screen.set_terminal_properties(colors=256)

        if enable_borders:
            self.toggle_border()
        if enable_word_wrap:
            self.toggle_wrapping()
        if show_toolbar:
            self.toggle_toolbar()
        if show_filter_panel:
            self.toggle_filter_panel()

        self.loop.run()
