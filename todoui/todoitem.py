import urwid
from todolib.todo import Todo
from todoui.advanced_edit import AdvancedEdit

class TodoItem(urwid.Button):

    def __init__(self, todo, key_bindings, colorscheme, parent_ui, editing=False, wrapping='clip'):
        super(TodoItem, self).__init__("")
        self.todo = todo
        self.key_bindings = key_bindings
        self.wrapping = wrapping
        self.colorscheme = colorscheme
        self.parent_ui = parent_ui
        self.editing = editing
        # urwid.connect_signal(self, 'click', callback)
        if editing: self.edit_item()
        else: self.update_todo()

    def selectable(self):
        return True

    def update_todo(self):
        if self.parent_ui.searching and self.parent_ui.search_string:
            text = urwid.Text(self.todo.highlight_search_matches(), wrap=self.wrapping)
        else:
            text = urwid.Text(self.todo.colored, wrap=self.wrapping)

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
        self.editing = False
        self.todo.update(self._w.original_widget.edit_text.strip())
        self.update_todo()
        self.parent_ui.todo_changed()

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
