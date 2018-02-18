import urwid
import collections
from todoui.components_ui import ViListBox

class MainHelp:

    def create_help_panel(key_bindings):
        key_column_width = 12
        header_highlight = 'plain_selected'
        return urwid.AttrMap(
            urwid.LineBox(
                urwid.Padding(
                    ViListBox(key_bindings,
                              [urwid.Divider()] +

                              [urwid.AttrWrap(urwid.Text("""
General
""".strip()), header_highlight)] +
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - show / hide this help message
{1} - quit and save
{2} - show / hide toolbar
{3} - toggle word wrap
{4} - toggle borders on todo items
{5} - save current todo file
{6} - reload the todo file (discarding changes)
""".format(
                            key_bindings["toggle-help"].ljust(key_column_width),
                            key_bindings["quit"].ljust(key_column_width),
                            key_bindings["toggle-toolbar"].ljust(key_column_width),
                            key_bindings["toggle-wrapping"].ljust(key_column_width),
                            key_bindings["toggle-borders"].ljust(key_column_width),
                            key_bindings["save"].ljust(key_column_width),
                            key_bindings["reload"].ljust(key_column_width),
                        ))] +

                        [urwid.AttrWrap(urwid.Text("""
Movement
""".strip()), header_highlight)] +
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - select any todo, checkbox or button
{1} - move selection down
{2} - move selection up
{3} - move selection to the top item
{4} - move selection to the bottom item
{5} - move selection between todos and filter panel
{6}
{7} - toggle focus between todos, filter panel, and toolbar
""".format(
                            "mouse click".ljust(key_column_width),
                            key_bindings["down"].ljust(key_column_width),
                            key_bindings["up"].ljust(key_column_width),
                            key_bindings["top"].ljust(key_column_width),
                            key_bindings["bottom"].ljust(key_column_width),
                            key_bindings["left"].ljust(key_column_width),
                            key_bindings["right"].ljust(key_column_width),
                            key_bindings["change-focus"].ljust(key_column_width),
                        ))] +

                        [urwid.AttrWrap(urwid.Text("""
Manipulating Todo Items
""".strip()), header_highlight)] +
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - complete / un-complete selected todo item
{1} - archive completed todo items to done.txt (if specified)
{2} - add a new todo to the end of the list
{3} - add a todo after the selected todo (when not filtering)
{4} - add a todo before the selected todo (when not filtering)
{5} - edit the selected todo
{6} - delete the selected todo
{7} - swap with item below
{8} - swap with item above
{9} - change due (add)
{10} - change due (subtract)
""".format(
                            key_bindings["toggle-complete"].ljust(key_column_width),
                            key_bindings["archive"].ljust(key_column_width),
                            key_bindings["append"].ljust(key_column_width),
                            key_bindings["insert-after"].ljust(key_column_width),
                            key_bindings["insert-before"].ljust(key_column_width),
                            key_bindings["edit"].ljust(key_column_width),
                            key_bindings["delete"].ljust(key_column_width),
                            key_bindings["swap-down"].ljust(key_column_width),
                            key_bindings["swap-up"].ljust(key_column_width),
                            key_bindings["add-due"].ljust(key_column_width),
                            key_bindings["subtract-due"].ljust(key_column_width),
                        ))] +

                        [urwid.AttrWrap(urwid.Text("""
While Editing a Todo
""".strip()), header_highlight)] +
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - tab complete contexts and projects
{1} - save todo item
{2} - move cursor left and right
{3}
{4} - move cursor backwards (left) by one word
{5} - move cursor forwards (right) by one word
{6} - move cursor the beginning or end of the line
{7}
{8} - delete one word backwards
{9} - delete from the cursor to the end of the line
{10} - delete from the cursor to the beginning of the line
{11} - paste last deleted text
""".format(
                            key_bindings["edit-complete"].ljust(key_column_width),
                            key_bindings["edit-save"].ljust(key_column_width),
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
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - toggle sort order (Unsorted, Ascending, Descending)
               sort order is saved on quit
""".format(
                            key_bindings["toggle-sorting"].ljust(key_column_width),
                        ))] +
                        [urwid.AttrWrap(urwid.Text("""
Filtering
""".strip()), header_highlight)] +
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - switch context
{1} - open / close the filtering panel
{2} - clear any active filters
""".format(
                            key_bindings["toggle-context"].ljust(key_column_width),
                            key_bindings["toggle-filter"].ljust(key_column_width),
                            key_bindings["clear-filter"].ljust(key_column_width),
                        ))] +
                        [urwid.AttrWrap(urwid.Text("""
Searching
""".strip()), header_highlight)] +
                        # [ urwid.Divider(u'─') ] +

                        [urwid.Text("""
{0} - start search
{1} - clear search
""".format(
                            key_bindings["search"].ljust(key_column_width),
                            key_bindings["search-clear"].ljust(key_column_width),
                        ))]
                    ),
                    left=1, right=1, min_width=10), title='Key Bindings'), 'default')
