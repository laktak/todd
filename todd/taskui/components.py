import urwid
from todd.tasklib.util import Util


class EntryWidget(urwid.Edit):

    def __init__(self, edit_text, on_enter):
        self.on_enter = on_enter
        super(EntryWidget, self).__init__(edit_text=edit_text)

    def keypress(self, size, key):
        if key == "enter": self.on_enter(self.edit_text)
        else: return super(EntryWidget, self).keypress(size, key)


class MenuItem(urwid.Text):
    def __init__(self, caption, on_enter=None):
        urwid.Text.__init__(self, caption)
        self.on_enter = on_enter

    def keypress(self, size, key):
        if key == "enter" and self.on_enter:
            self.on_enter()
        else:
            return key

    def selectable(self):
        return True


class ViColumns(urwid.Columns):

    def __init__(self, key_bindings, widget_list, dividechars=0, focus_column=None, min_width=1, box_columns=None):
        super(ViColumns, self).__init__(widget_list, dividechars, focus_column, min_width, box_columns)

        self._command_map = Util.define_keys(urwid.command_map.copy(), key_bindings, [
            ("down", urwid.CURSOR_DOWN),
            ("up", urwid.CURSOR_UP),
            ("home", urwid.CURSOR_MAX_LEFT),
            ("end", urwid.CURSOR_MAX_RIGHT),
        ])


class ViListBox(urwid.ListBox):

    def __init__(self, key_bindings, *args, **kwargs):
        super(ViListBox, self).__init__(*args, **kwargs)

        self.key_bindings = key_bindings
        self._command_map = Util.define_keys(urwid.command_map.copy(), key_bindings, [
            ("down", urwid.CURSOR_DOWN),
            ("up", urwid.CURSOR_UP),
            ("home", urwid.CURSOR_MAX_LEFT),
            ("end", urwid.CURSOR_MAX_RIGHT),
            ("page-up", urwid.CURSOR_PAGE_UP),
            ("page-down", urwid.CURSOR_PAGE_DOWN),
        ])

    def listbox_count(self):
        return len(self.body)

    def _keypress_max_left(self):
        return self.move_top()

    def _keypress_max_right(self):
        return self.move_bottom()

    def move_top(self):
        for i, item in enumerate(self.body):
            if item.selectable():
                self.set_focus(i)
                return

    def move_bottom(self):
        for i, item in reversed(list(enumerate(self.body))):
            if item.selectable():
                self.set_focus(i)
                return

    def move_offs(self, offs):
        w, pos = self.get_focus()
        d = -1 if offs < 0 else 1
        offs = abs(offs)
        item = None
        while offs > 0:
            pos += d
            if pos < 0 or pos >= len(self.body):
                item = None
                break
            item = self.body[pos]
            if not item: break
            if item.selectable(): offs -= 1
        if item:
            self.set_focus(pos)

    def keypress(self, size, key):
        key = super(ViListBox, self).keypress(size, key)
        if self.key_bindings.is_bound_to(key, "home"): self.move_top()
        elif self.key_bindings.is_bound_to(key, "end"): self.move_bottom()
        else: return key
