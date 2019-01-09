#!/usr/bin/env python
import sys

from todd.main import main

if sys.version_info < (3, 6):
    sys.exit("Python < 3.6 is not supported")


main()
