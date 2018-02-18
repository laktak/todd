import urwid
from todolib.todo import Todo

class EntryWidget(urwid.Edit):

    def __init__(self, edit_text, on_enter):
        self.on_enter = on_enter
        super(EntryWidget, self).__init__(edit_text=edit_text)

    def keypress(self, size, key):
        if key == 'enter':
            self.on_enter(self.edit_text)
        return super(EntryWidget, self).keypress(size, key)


class MenuItem(urwid.Text):
    def __init__(self, caption, on_enter=None):
        urwid.Text.__init__(self, caption)
        self.on_enter = on_enter

    def keypress(self, size, key):
        if key == 'enter' and self.on_enter:
            self.on_enter()
        else:
            return key

    def selectable(self):
        return True


class TodoWidget(urwid.Button):

    def __init__(self, todo, key_bindings, colorscheme, parent_ui, editing=False, wrapping='clip', border='no border'):
        super(TodoWidget, self).__init__("")
        self.todo = todo
        self.key_bindings = key_bindings
        self.wrapping = wrapping
        self.border = border
        self.colorscheme = colorscheme
        self.parent_ui = parent_ui
        self.editing = editing
        # urwid.connect_signal(self, 'click', callback)
        if editing:
            self.edit_item()
        else:
            self.update_todo()

    def selectable(self):
        return True

    def update_todo(self):
        if self.parent_ui.searching and self.parent_ui.search_string:
            text = urwid.Text(self.todo.highlight_search_matches(), wrap=self.wrapping)
        else:
            if self.border == 'bordered':
                text = urwid.Text(self.todo.highlight(show_due_date=False, show_contexts=False, show_projects=False), wrap=self.wrapping)
            else:
                text = urwid.Text(self.todo.colored, wrap=self.wrapping)

        if self.border == 'bordered':
            lt = ''
            if self.todo.due_date:
                lt = ('due_date', "due:{0}".format(self.todo.due_date))
            t = []
            t.append(('context', ' '.join(self.todo.contexts)))
            if self.todo.contexts and self.todo.projects:
                t.append(' ')
            t.append(('project', ' '.join(self.todo.projects)))
            bc = 'plain'
            if self.todo.priority and self.todo.priority in "ABCDEF":
                bc = "priority_{0}".format(self.todo.priority.lower())
            text = TodoLineBox(text, top_left_title=lt, bottom_right_title=t, border_color=bc, )
        self._w = urwid.AttrMap(urwid.AttrMap(
            text,
            None, 'selected'),
            None, self.colorscheme.focus_map)

    def edit_item(self):
        self.editing = True
        self.edit_widget = AdvancedEdit(self.parent_ui, self.key_bindings, caption="", edit_text=self.todo.raw)
        self.edit_widget.setCompletionMethod(self.completions)
        self._w = urwid.AttrMap(self.edit_widget, 'plain_selected')

    def completions(self, text, completion_data={}):
        space = text.rfind(" ")
        start = text[space + 1:]
        words = self.parent_ui.todos.all_contexts() + self.parent_ui.todos.all_projects()
        try:
            start_idx = words.index(completion_data['last_word']) + 1
            if start_idx == len(words):
                start_idx = 0
        except (KeyError, ValueError):
            start_idx = 0
        for idx in list(range(start_idx, len(words))) + list(range(0, start_idx)):
            if words[idx].lower().startswith(start.lower()):
                completion_data['last_word'] = words[idx]
                return text[:space + 1] + words[idx] + (': ' if space < 0 else '')
        return text

    def save_item(self):
        self.todo.update(self._w.original_widget.edit_text.strip())
        self.update_todo()
        if self.parent_ui.filter_panel_is_open:
            self.parent_ui.update_filters(new_contexts=self.todo.contexts, new_projects=self.todo.projects)
        self.editing = False

    def keypress(self, size, key):
        if self.editing:
            if key in ['down', 'up']:
                return None  # don't pass up or down to the ListBox
            elif self.key_bindings.is_binded_to(key, 'save-item'):
                self.save_item()
                return key
            else:
                return self._w.keypress(size, key)
        else:
            if self.key_bindings.is_binded_to(key, 'edit'):
                self.edit_item()
                return key
            else:
                return key


class TodoLineBox(urwid.WidgetDecoration, urwid.WidgetWrap):

    def __init__(self, original_widget, top_left_title="", bottom_right_title="", border_color='plain',
                 tlcorner=u'┌', tline=u'─', lline=u'│',
                 trcorner=u'┐', blcorner=u'└', rline=u'│',
                 bline=u'─', brcorner=u'┘'):
        """
        Draw a line around original_widget.

        Use 'title' to set an initial title text with will be centered
        on top of the box.

        You can also override the widgets used for the lines/corners:
            tline: top line
            bline: bottom line
            lline: left line
            rline: right line
            tlcorner: top left corner
            trcorner: top right corner
            blcorner: bottom left corner
            brcorner: bottom right corner

        """

        tline, bline = urwid.AttrMap(urwid.Divider(tline), border_color), urwid.AttrMap(urwid.Divider(bline), border_color)
        lline, rline = urwid.AttrMap(urwid.SolidFill(lline), border_color), urwid.AttrMap(urwid.SolidFill(rline), border_color)
        tlcorner, trcorner = urwid.AttrMap(urwid.Text(tlcorner), border_color), urwid.AttrMap(urwid.Text(trcorner), border_color)
        blcorner, brcorner = urwid.AttrMap(urwid.Text(blcorner), border_color), urwid.AttrMap(urwid.Text(brcorner), border_color)

        self.ttitle_widget = urwid.Text(top_left_title)
        self.tline_widget = urwid.Columns([
            ('fixed', 1, tline),
            ('flow', self.ttitle_widget),
            tline,
        ])
        self.btitle_widget = urwid.Text(bottom_right_title)
        self.bline_widget = urwid.Columns([
            bline,
            ('flow', self.btitle_widget),
            ('fixed', 1, bline),
        ])

        middle = urwid.Columns([
            ('fixed', 1, lline),
            original_widget,
            ('fixed', 1, rline),
        ], box_columns=[0, 2], focus_column=1)

        top = urwid.Columns([
            ('fixed', 1, tlcorner),
            self.tline_widget,
            ('fixed', 1, trcorner)
        ])

        bottom = urwid.Columns([
            ('fixed', 1, blcorner),
            self.bline_widget,
            ('fixed', 1, brcorner)
        ])

        pile = urwid.Pile([('flow', top), middle, ('flow', bottom)], focus_item=1)

        urwid.WidgetDecoration.__init__(self, original_widget)
        urwid.WidgetWrap.__init__(self, pile)


class ViColumns(urwid.Columns):

    def __init__(self, key_bindings, widget_list, dividechars=0, focus_column=None, min_width=1, box_columns=None):
        super(ViColumns, self).__init__(widget_list, dividechars, focus_column, min_width, box_columns)
        command_map = urwid.command_map.copy()

        keys = key_bindings.getKeyBinding('right')
        for key in keys:
            command_map[key] = urwid.CURSOR_RIGHT
        keys = key_bindings.getKeyBinding('left')
        for key in keys:
            command_map[key] = urwid.CURSOR_LEFT

        self._command_map = command_map


class ViListBox(urwid.ListBox):

    def __init__(self, key_bindings, *args, **kwargs):
        super(ViListBox, self).__init__(*args, **kwargs)
        command_map = urwid.command_map.copy()

        keys = key_bindings.getKeyBinding('down')
        for key in keys:
            command_map[key] = urwid.CURSOR_DOWN
        keys = key_bindings.getKeyBinding('up')
        for key in keys:
            command_map[key] = urwid.CURSOR_UP

        self._command_map = command_map
