# -*- coding: utf-8 -*-

"""
todd
====

*todd* is an interactive console TODO manager with VI key bindings.
"""

from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand
import sys
import tasklib


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


setup(name=NAME,
      version=tasklib.version,
      author="Christian Zangl",
      author_email="laktak@cdak.net",
      url="https://github.com/laktak/todd",
      description="An interactive terminal based todo.txt file editor",
      long_description=long_description,
      keywords="todotxt, todo.txt, todo, terminal, urwid, curses, console",
      packages=find_packages(exclude=["tasklib/test*"]),
      include_package_data=True,
      entry_points={
          "console_scripts": ["todd = taskui.cli:main"]
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
      install_requires=["setuptools", "docopt>=0.6.2", "urwid>=1.2.1"],
      tests_require=["pytest"],
      cmdclass={"test": PyTest})
