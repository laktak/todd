# -*- coding: utf-8 -*-

"""
todd
====

*todd* is an interactive console TODO manager with VI key bindings.
"""

import sys

if sys.version_info < (3, 6):
    sys.exit('Please install with Python >= 3.6')

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todd', '__init__.py')) as fd:
    version = [line.split()[-1].strip("\"") for line in fd if line.startswith('version')]
if not version: raise Exception("Missing version!")


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


NAME = "todd"

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = __doc__


setup(
    name=NAME,
    version=version[0],
    author="Christian Zangl",
    author_email="laktak@cdak.net",
    url="https://github.com/laktak/todd",
    description="An interactive terminal based todo.txt file editor",
    long_description=long_description,
    keywords="todotxt, todo.txt, todo, terminal, urwid, curses, console",
    packages=find_packages(exclude=["todd/tasklib/test"]),
    include_package_data=True,
    entry_points={
        "console_scripts": ["todd = todd.main:main"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console :: Curses",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3.6",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires='>=3.6.0',
    install_requires=["setuptools", "docopt>=0.6.2", "urwid>=1.3.0", "urwid_viedit>=0.1.0", "watchdog>=0.8.3"],
    tests_require=["pytest"],
    cmdclass={"test": PyTest})
