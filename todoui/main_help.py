import urwid

from textwrap import dedent
from todoui import ViListBox


class MainHelp:

    def create_help_panel(key_bindings):

        key_column_width = 12
        header_highlight = "plain_selected"
        items = (
            [urwid.Divider()] +
            [urwid.Text("Key Bindings", align="center")] +
            [urwid.Divider()] +

            [urwid.AttrWrap(urwid.Text("General"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - show / hide this help message
                {1} - quit and save
                {2} - toggle word wrap
                {3} - save current todo file
                {4} - reload the todo file (discarding changes)
                {5} - archive done items to done.txt
                {6} - undo archive for the last item (repeat as required)
                """).format(
                key_bindings["toggle-help"].ljust(key_column_width),
                key_bindings["quit"].ljust(key_column_width),
                key_bindings["toggle-wrapping"].ljust(key_column_width),
                key_bindings["save"].ljust(key_column_width),
                key_bindings["reload"].ljust(key_column_width),
                key_bindings["archive"].ljust(key_column_width),
                key_bindings["undo-archive"].ljust(key_column_width),
            ))] +

            [urwid.AttrWrap(urwid.Text("Movement"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - move selection down
                {1} - move selection up
                {2} - move selection to the top item
                {3} - move selection to the bottom item
                {4} - move focus between panels
                {5}
                """.format(
                key_bindings["down"].ljust(key_column_width),
                key_bindings["up"].ljust(key_column_width),
                key_bindings["home"].ljust(key_column_width),
                key_bindings["end"].ljust(key_column_width),
                key_bindings["left"].ljust(key_column_width),
                key_bindings["right"].ljust(key_column_width),
            )))] +

            [urwid.AttrWrap(urwid.Text("Todo Items"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - add a new todo item
                {1} - edit the selected item
                {2} - higher priority
                {3} - lower priority
                {4} - mark / unmark selected item done
                {5} - delete the selected item
                {6} - change due (add)
                {7} - change due (subtract)
                """.format(
                key_bindings["new"].ljust(key_column_width),
                key_bindings["edit"].ljust(key_column_width),
                key_bindings["priority-lower"].ljust(key_column_width),
                key_bindings["priority-higher"].ljust(key_column_width),
                key_bindings["toggle-done"].ljust(key_column_width),
                key_bindings["delete"].ljust(key_column_width),
                key_bindings["add-due"].ljust(key_column_width),
                key_bindings["subtract-due"].ljust(key_column_width),
            )))] +

            [urwid.AttrWrap(urwid.Text("While Editing a Todo"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - tab complete contexts and projects
                {1} - move cursor left
                {2} - move cursor right
                {3} - move cursor backwards (left) by one word
                {4} - move cursor forwards (right) by one word
                {5} - move cursor the beginning of the line
                {6} - move cursor the end of the line
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
            )))] +

            [urwid.AttrWrap(urwid.Text("Search & Sort"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - switch context
                {1} - start search
                {2} - clear search
                {3} - toggle sort order
                """.format(
                key_bindings["switch-context"].ljust(key_column_width),
                key_bindings["search"].ljust(key_column_width),
                key_bindings["search-clear"].ljust(key_column_width),
                key_bindings["toggle-sort-order"].ljust(key_column_width),
            )))]
        )

        return urwid.AttrMap(
            urwid.Padding(
                ViListBox(key_bindings, items),
                left=1, right=1, min_width=10), "dialog_color")
