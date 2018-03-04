
"""todd

Usage:
  todd [--config FILE] [TODOFILE] [DONEFILE]
  todd (-h | --help)
  todd --version
  todd --show-default-bindings

Options:
  -c FILE --config=FILE               Path to your todd configuraton file [default: ~/.toddrc]
  -h --help                           Show this screen.
  --version                           Show version.
  --show-default-bindings             Show default keybindings in config parser format
"""

import sys

if sys.version_info < (3, 6):
    sys.exit('Python < 3.6 is not supported')

import os
from collections import OrderedDict
from docopt import docopt
import todd
from todd.tasklib import Tasklist
from todd.taskui import MainUI, ColorScheme, KeyBindings
import configparser


def exit_with_error(message):
    sys.stderr.write(message.strip(" \n") + "\n")
    print(__doc__.split("\n\n")[1])
    exit(1)


def get_real_path(filename, description):
    # expand enviroment variables and username, get canonical path
    file_path = os.path.realpath(os.path.expanduser(os.path.expandvars(filename)))

    if os.path.isdir(file_path):
        exit_with_error("ERROR: Specified {0} file is a directory.".format(description))

    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if os.path.isdir(directory):
            # directory exists, but no todo.txt file - create an empty one
            open(file_path, "a").close()
        else:
            exit_with_error(
                ("ERROR: The directory: '{0}' for '{1}' does not exist\n").format(directory, file_path)
            )

    return file_path


def get_boolean_config_option(cfg, section, option, default=False):
    value = dict(cfg.items(section)).get(option, default)
    if (type(value) != bool and
        (str(value).lower() == "true" or
         str(value).lower() == "1")):
        value = True
    else:
        # If present but is not True or 1
        value = False
    return value


def main():

    # Parse command line
    arguments = docopt(__doc__, version=todd.version)

    # Parse config file
    cfg = configparser.ConfigParser(allow_no_value=True)
    cfg.add_section("keys")

    if arguments["--show-default-bindings"]:
        d = {k: ", ".join(v) for k, v in KeyBindings({}).key_bindings.items()}
        cfg._sections["keys"] = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
        cfg.write(sys.stdout)
        exit(0)

    cfg.add_section("settings")
    cfg.read(os.path.expanduser(arguments["--config"]))

    # Load keybindings specified in the [keys] section of the config file
    keyBindings = KeyBindings(dict(cfg.items("keys")))

    # load the colorscheme defined in the user config, else load the default scheme
    colorscheme = ColorScheme(dict(cfg.items("settings")).get("colorscheme", "default"), cfg)

    # Load the todo.txt file specified in the [settings] section of the config file
    # a todo.txt file on the command line takes precedence
    todotxt_file = dict(cfg.items("settings")).get("file", arguments["TODOFILE"])
    if arguments["TODOFILE"]:
        todotxt_file = arguments["TODOFILE"]

    if todotxt_file is None:
        exit_with_error((
            "ERROR: No todo file specified. Either specify one as an argument " +
            " on the command line or set it in your configuration file ({0}).").format(arguments["--config"])
        )

    # Load the done.txt file specified in the [settings] section of the config file
    # a done.txt file on the command line takes precedence
    donetxt_file = dict(cfg.items("settings")).get("archive", arguments["DONEFILE"])
    if arguments["DONEFILE"]:
        donetxt_file = arguments["DONEFILE"]

    todotxt_file_path = get_real_path(todotxt_file, "todo.txt")

    if donetxt_file is not None:
        donetxt_file_path = get_real_path(donetxt_file, "done.txt")
    else:
        donetxt_file_path = None

    try:
        tasklist = Tasklist.open_file(todotxt_file_path, donetxt_file_path)
    except Exception:
        exit_with_error((
            "ERROR: unable to open {0}\n\nEither specify one as an argument on the " +
            "command line or set it in your configuration file ({1}).").format(todotxt_file_path, arguments["--config"])
        )

    enable_word_wrap = get_boolean_config_option(cfg, "settings", "enable-word-wrap")

    view = MainUI(tasklist, keyBindings, colorscheme)
    view.main(enable_word_wrap)  # start up the urwid UI event loop

    # Final save
    view.tasklist.save()

    exit(0)


if __name__ == "__main__":
    main()
