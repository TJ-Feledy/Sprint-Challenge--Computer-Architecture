#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

program = sys.argv

cpu = CPU()

cpu.load(program)
cpu.run()