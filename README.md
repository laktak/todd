# todd

*todd* is an interactive console TODO manager with VI key bindings.

It provides a minimalistic interface with a view on your todo list, following in the spirit of spirit of [ranger](https://ranger.github.io/) and [mutt](http://www.mutt.org/).

The file format conforms to [todo.txt](https://github.com/todotxt/todo.txt#readme). This means you have full control over your data and can choose to store it locally or in the cloud (like Dropbox). You can use different applications to access your todos on your desktop or mobile devices.

Thanks to the creator and contributors of [todotxt-machine](https://github.com/AnthonyDiGirolamo/todotxt-machine/tree/04a0306ea30c2645f2474da5830852ccd8e49082) for providing the basis for this project.

## Features

- View your todos in a column formatted list with relative due dates
- Switch context (only view tasks that you can work on)
- Sort by due date or priority
- Search/filter
- Edit in plain text with tab completion or adjust priority and due

## Requirements

Python 3.6 on Linux or macOS
[urwid](http://excess.org/urwid/)

## Installation

### Using [pip](https://pypi.python.org/pypi/pip)

    pip install todd

### Manually

Download or clone this repo and run the `todd.py` script.

    git clone https://github.com/laktak/todd.git
    cd todd
    ./todd.py

## Command Line Options

    todd

    Usage:
      todd
      todd TODOFILE [DONEFILE]
      todd [--config FILE]
      todd (-h | --help)
      todd --version
      todd --show-default-bindings

    Options:
      -c FILE --config=FILE               Path to your todd configuraton file [default: ~/.toddrc]
      -h --help                           Show this screen.
      --version                           Show version.
      --show-default-bindings             Show default keybindings in config parser format
                                          Add this to your config file and edit to customize



## Config File

You can tell todd to use the same todo.txt file whenever it starts up by adding a ``file`` entry to the `~/.toddrc` file. If you want to archive done tasks, you can specify a done.txt file using an ``archive`` entry. You can also set you preferred colorscheme or even define new themes.

Here is a short example:

```
[settings]
file = ~/todo.txt
archive = ~/done.txt
enable-word-wrap = True
colorscheme = myawesometheme
```

## Color Schemes

Here is a config file with a complete colorscheme definition:

```
[settings]
file = ~/todo.txt
colorscheme = myawesometheme

[colorscheme-myawesometheme]
plain=h250
...
```

You can add colorschemes by adding sections with names that start with `colorscheme-`. Then under the `[settings]` section you can say which colorscheme you want to use.

The format for a color definitions is:

```
name=[foreground],[background]
```

Foreground and background colors are follow the 256 color formats [defined by urwid](http://urwid.org/manual/displayattributes.html#color-foreground-and-background-colors). You can see all the colors defined [here](http://urwid.org/examples/index.html#palette-test-py).

## Key Bindings

See active key bindings with `h` or `?` in todd.

You can customize any key binding by adding a setting to the `[keys]` section of your config file `~/.toddrc`.

For a list of the default key bindings run:

```
todd --show-default-bindings
```
