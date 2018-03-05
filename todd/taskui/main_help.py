import urwid

from textwrap import dedent
from todd.taskui import ViListBox


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
                {0} - show / hide help
                {1} - quit
                {2} - reload the todo file
                {3} - archive done tasks to done.txt
                {4} - undo archive for the last task (repeat as required)
                """).format(
                key_bindings["toggle-help"].ljust(key_column_width),
                key_bindings["quit"].ljust(key_column_width),
                key_bindings["reload"].ljust(key_column_width),
                key_bindings["archive"].ljust(key_column_width),
                key_bindings["undo-archive"].ljust(key_column_width),
            ))] +

            [urwid.AttrWrap(urwid.Text("View"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - toggle view
                {1} - toggle word wrap
                """).format(
                key_bindings["toggle-view"].ljust(key_column_width),
                key_bindings["toggle-wrapping"].ljust(key_column_width),
            ))] +

            [urwid.AttrWrap(urwid.Text("Movement"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - move selection down
                {1} - move selection up
                {2} - move selection to the top
                {3} - move selection to the bottom
                {4} - move page down
                {5} - move page up
                """.format(
                key_bindings["down"].ljust(key_column_width),
                key_bindings["up"].ljust(key_column_width),
                key_bindings["home"].ljust(key_column_width),
                key_bindings["end"].ljust(key_column_width),
                key_bindings["page-down"].ljust(key_column_width),
                key_bindings["page-up"].ljust(key_column_width),
            )))] +

            [urwid.AttrWrap(urwid.Text("Tasks"), header_highlight)] +
            [urwid.Text(dedent("""\
                {0} - add a new task
                {1} - edit the selected task
                {2} - raise priority
                {3} - lower priority
                {4} - mark / unmark selected task done
                {5} - delete the selected task
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
