import urwid

# Modified from http://wiki.goffi.org/wiki/Urwid-satext/en


class AdvancedEdit(urwid.Edit):
    """Edit box with some custom improvments
    new chars:
              - C-a: like "home"
              - C-e: like "end"
              - C-k: remove everything on the right of the cursor
              - C-w: remove the word on the back"""

    def __init__(self, parent_ui, key_bindings, *args, **kwargs):
        self.parent_ui = parent_ui
        self.key_bindings = key_bindings
        super(AdvancedEdit, self).__init__(*args, **kwargs)

    def setCompletionMethod(self, callback):
        """Define method called when completion is asked
        @callback: method with 2 arguments:
                    - the text to complete
                    - if there was already a completion, a dict with
                        - "completed":last completion
                        - "completion_pos": cursor position where the completion starts
                        - "position": last completion cursor position
                      this dict must be used (and can be filled) to find next completion)
                   and which return the full text completed"""
        self.completion_cb = callback
        self.completion_data = {}

    def keypress(self, size, key):
        if self.key_bindings.is_bound_to(key, "edit-home"):
            self.set_edit_pos(0)  # move to the beginning of the line
        elif self.key_bindings.is_bound_to(key, "edit-end"):
            self.set_edit_pos(len(self.edit_text) - 1)  # move to the end of the line
        elif self.key_bindings.is_bound_to(key, "edit-delete-end"):
            self.parent_ui.yanked_text = self.edit_text[self.edit_pos:]
            self._delete_highlighted()
            self.set_edit_text(self.edit_text[:self.edit_pos])
        elif self.key_bindings.is_bound_to(key, "edit-paste"):
            self.set_edit_text(
                self.edit_text[:self.edit_pos] +
                self.parent_ui.yanked_text +
                self.edit_text[self.edit_pos:])
            self.set_edit_pos(self.edit_pos + len(self.parent_ui.yanked_text))
        elif self.key_bindings.is_bound_to(key, "edit-delete-word"):
            before = self.edit_text[:self.edit_pos]
            pos = before.rstrip().rfind(" ") + 1
            self.parent_ui.yanked_text = self.edit_text[pos:self.edit_pos]
            self.set_edit_text(before[:pos] + self.edit_text[self.edit_pos:])
            self.set_edit_pos(pos)
        elif self.key_bindings.is_bound_to(key, "edit-delete-beginning"):
            before = self.edit_text[:self.edit_pos]
            self.parent_ui.yanked_text = self.edit_text[:self.edit_pos]
            self.set_edit_text(self.edit_text[self.edit_pos:])
            self.set_edit_pos(0)
        elif self.key_bindings.is_bound_to(key, "edit-word-left"):
            before = self.edit_text[:self.edit_pos]
            pos = before.rstrip().rfind(" ") + 1
            self.set_edit_pos(pos)
        elif self.key_bindings.is_bound_to(key, "edit-word-right"):
            after = self.edit_text[self.edit_pos:]
            pos = after.rstrip().find(" ") + 1
            self.set_edit_pos(self.edit_pos + pos)
        elif self.key_bindings.is_bound_to(key, "edit-complete"):
            try:
                before = self.edit_text[:self.edit_pos]
                if self.completion_data:
                    if (not self.completion_data["completed"] or
                            self.completion_data["position"] != self.edit_pos or
                            not before.endswith(self.completion_data["completed"])):
                        self.completion_data.clear()
                    else:
                        before = before[:-len(self.completion_data["completed"])]
                complet = self.completion_cb(before, self.completion_data)
                self.completion_data["completed"] = complet[len(before):]
                self.set_edit_text(complet + self.edit_text[self.edit_pos:])
                self.set_edit_pos(len(complet))
                self.completion_data["position"] = self.edit_pos
                return
            except AttributeError:
                # No completion method defined
                pass
        return super(AdvancedEdit, self).keypress(size, key)
