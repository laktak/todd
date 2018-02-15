#!/usr/bin/env python
# coding=utf-8
import sys
import subprocess
import termios
import re
import fcntl
import struct


class TerminalOperations:
    """For interacting with the terminal"""

    _escape_sequence_regex = re.compile(r'\x1b\[[0-9;]*m')
    _screen_size_regex = re.compile(r'\[8;(.*);(.*)t')

    @staticmethod
    def foreground_color(index):
        return "\x1B[38;5;{0}m".format(index)

    @staticmethod
    def background_color(index):
        return "\x1B[48;5;{0}m".format(index)

    @staticmethod
    def clear_formatting():
        return "\x1B[m"

    def __init__(self, use_tput=False):
        # self.window = curses.initscr()
        self.update_screen_size(use_tput)

    def update_screen_size(self, use_tput=False):
        self.columns, self.rows = self.screen_size(use_tput)

    def output(self, text):
        sys.stdout.write(text)

    def hide_cursor(self):
        # subprocess.check_output(["tput", "civis"])
        self.output('\x1b[?25l')

    def show_cursor(self):
        # subprocess.check_output(["tput", "cnorm"])
        self.output('\x1b[34h\x1b[?25h')

    def clear_screen(self):
        self.output("\x1B[2J")

    def screen_size(self, use_tput=False):
        # Method: Usint tput
        if use_tput:
            return (int(subprocess.check_output(["tput", "cols"])), int(subprocess.check_output(["tput", "lines"])))
        else:
            # this is how urwid does it in raw_terminal display mode
            buf = fcntl.ioctl(0, termios.TIOCGWINSZ, ' ' * 4)
            y, x = struct.unpack('hh', buf)
            return x, y

    def move_cursor(self, row, column):
        self.output("\x1B[{0};{1}H".format(row, column))

    def move_cursor_home(self):
        self.output("\x1B[[H")

    def move_cursor_next_line(self):
        self.output("\x1B[E")

    @staticmethod
    def length_ignoring_escapes(line):
        return len(line) - sum([len(i) for i in TerminalOperations._escape_sequence_regex.findall(line)])

    @staticmethod
    def ljust_with_escapes(line, columns, string_length=0):
        length = TerminalOperations.length_ignoring_escapes(line) if string_length == 0 else string_length
        if length < columns:
            line += " " * (columns - length)
        return line
