import urwid
import collections
from todoui.components import ViListBox

class MainHelp:

    def create_help_panel(key_bindings):

        key_column_width = 12
        header_highlight = 'plain_selected'
        items = (
        [urwid.Text('Key Bindings', align='center')] +

        # [urwid.Divider()] +

        [urwid.AttrWrap(urwid.Text("""
General
""".strip()), header_highlight)] +

        [urwid.Text("""
{0} - show / hide this help message
{1} - quit and save
{2} - toggle word wrap
{3} - save current todo file
{4} - reload the todo file (discarding changes)
""".format(
            key_bindings["toggle-help"].ljust(key_column_width),
            key_bindings["quit"].ljust(key_column_width),
            key_bindings["toggle-wrapping"].ljust(key_column_width),
            key_bindings["save"].ljust(key_column_width),
            key_bindings["reload"].ljust(key_column_width),
        ))] +

        [urwid.AttrWrap(urwid.Text("""
Movement
""".strip()), header_highlight)] +

        [urwid.Text("""
{0} - move selection down
{1} - move selection up
{2} - move selection to the top item
{3} - move selection to the bottom item
{4} - move focus between panels
{5}
""".format(
            key_bindings["down"].ljust(key_column_width),
            key_bindings["up"].ljust(key_column_width),
            key_bindings["top"].ljust(key_column_width),
            key_bindings["bottom"].ljust(key_column_width),
            key_bindings["left"].ljust(key_column_width),
            key_bindings["right"].ljust(key_column_width),
        ))] +

        [urwid.AttrWrap(urwid.Text("""
Manipulating Todo Items
""".strip()), header_highlight)] +

        [urwid.Text("""
{0} - mark / unmark selected item done
{1} - archive done items to done.txt (if specified)
{2} - add a new todo item
{3} - edit the selected item
{4} - delete the selected item
{5} - change due (add)
{6} - change due (subtract)
{7} - higher priority
{8} - lower priority
""".format(
            key_bindings["toggle-done"].ljust(key_column_width),
            key_bindings["archive"].ljust(key_column_width),
            key_bindings["new"].ljust(key_column_width),
            key_bindings["edit"].ljust(key_column_width),
            key_bindings["delete"].ljust(key_column_width),
            key_bindings["add-due"].ljust(key_column_width),
            key_bindings["subtract-due"].ljust(key_column_width),
            key_bindings["priority-lower"].ljust(key_column_width),
            key_bindings["priority-higher"].ljust(key_column_width),
        ))] +

        [urwid.AttrWrap(urwid.Text("""
While Editing a Todo
""".strip()), header_highlight)] +

        [urwid.Text("""
{0} - tab complete contexts and projects
{1} - move cursor left and right
{2}
{3} - move cursor backwards (left) by one word
{4} - move cursor forwards (right) by one word
{5} - move cursor the beginning or end of the line
{6}
{7} - delete one word backwards
{8} - delete from the cursor to the end of the line
{9} - delete from the cursor to the beginning of the line
{10} - paste last deleted text
""".format(
            key_bindings["edit-complete"].ljust(key_column_width),
            key_bindings["edit-move-left"].ljust(key_column_width),
            key_bindings["edit-move-right"].ljust(key_column_width),
            key_bindings["edit-word-left"].ljust(key_column_width),
            key_bindings["edit-word-right"].ljust(key_column_width),
            key_bindings["edit-home"].ljust(key_column_width),
            key_bindings["edit-end"].ljust(key_column_width),
            key_bindings["edit-delete-word"].ljust(key_column_width),
            key_bindings["edit-delete-end"].ljust(key_column_width),
            key_bindings["edit-delete-beginning"].ljust(key_column_width),
            key_bindings["edit-paste"].ljust(key_column_width),
        ))] +

        [urwid.AttrWrap(urwid.Text("""
Sorting
""".strip()), header_highlight)] +

        [urwid.Text("""
{0} - toggle sort order
""".format(
            key_bindings["toggle-sort-order"].ljust(key_column_width),
        ))] +
        [urwid.AttrWrap(urwid.Text("""
Searching
""".strip()), header_highlight)] +

        [urwid.Text("""
{0} - start search
{1} - clear search
{2} - switch context
""".format(
            key_bindings["search"].ljust(key_column_width),
            key_bindings["search-clear"].ljust(key_column_width),
            key_bindings["toggle-context"].ljust(key_column_width),
        ))])

        return urwid.AttrMap(
            urwid.Padding(
                ViListBox(key_bindings, items),
                left=1, right=1, min_width=10), 'dialog_color')
