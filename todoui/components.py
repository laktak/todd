import urwid

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
