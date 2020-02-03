#!/usr/bin/python3
# -*- coding:Utf-8 -*-

# PyScribus, python library for Scribus SLA
# Copyright (C) 2020 Étienne Nadji
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
ISO 216, international system for paper size.

A, B formats.

Yes, this is the module for A4 paper sizes.

See iso269paper module for C format.
See iso217paper module for RA, SRA formats.
"""

# Imports ===============================================================#

from pyscribus.common.math import FloatEnum, PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

# A format --------------------------------------

class A0(FloatEnum):
    WIDTH = 841 / PICA_TO_MM
    HEIGHT = 1189 / PICA_TO_MM

class A1(FloatEnum):
    WIDTH = 594 / PICA_TO_MM
    HEIGHT = 841 / PICA_TO_MM

class A2(FloatEnum):
    WIDTH = 420 / PICA_TO_MM
    HEIGHT = 594 / PICA_TO_MM

class A3(FloatEnum):
    WIDTH = 297 / PICA_TO_MM
    HEIGHT = 420 / PICA_TO_MM

class A4(FloatEnum):
    WIDTH = 210 / PICA_TO_MM
    HEIGHT = 297 / PICA_TO_MM

class A5(FloatEnum):
    WIDTH = 148 / PICA_TO_MM
    HEIGHT = 210 / PICA_TO_MM

class A6(FloatEnum):
    WIDTH = 105 / PICA_TO_MM
    HEIGHT = 148 / PICA_TO_MM

class A7(FloatEnum):
    WIDTH = 74 / PICA_TO_MM
    HEIGHT = 105 / PICA_TO_MM

class A8(FloatEnum):
    WIDTH = 52 / PICA_TO_MM
    HEIGHT = 74 / PICA_TO_MM

class A9(FloatEnum):
    WIDTH = 37 / PICA_TO_MM
    HEIGHT = 52 / PICA_TO_MM

class A10(FloatEnum):
    WIDTH = 26 / PICA_TO_MM
    HEIGHT = 37 / PICA_TO_MM

# B format --------------------------------------

class B0(FloatEnum):
    WIDTH = 1000 / PICA_TO_MM
    HEIGHT = 1414 / PICA_TO_MM

class B1(FloatEnum):
    WIDTH = 707 / PICA_TO_MM
    HEIGHT = 1000 / PICA_TO_MM

class B2(FloatEnum):
    WIDTH = 500 / PICA_TO_MM
    HEIGHT = 707 / PICA_TO_MM

class B3(FloatEnum):
    WIDTH = 353 / PICA_TO_MM
    HEIGHT = 500 / PICA_TO_MM

class B4(FloatEnum):
    WIDTH = 250 / PICA_TO_MM
    HEIGHT = 353 / PICA_TO_MM

class B5(FloatEnum):
    WIDTH = 176 / PICA_TO_MM
    HEIGHT = 250 / PICA_TO_MM

class B6(FloatEnum):
    WIDTH = 125 / PICA_TO_MM
    HEIGHT = 176 / PICA_TO_MM

class B7(FloatEnum):
    WIDTH = 88 / PICA_TO_MM
    HEIGHT = 125 / PICA_TO_MM

class B8(FloatEnum):
    WIDTH = 62 / PICA_TO_MM
    HEIGHT = 88 / PICA_TO_MM

class B9(FloatEnum):
    WIDTH = 44 / PICA_TO_MM
    HEIGHT = 62 / PICA_TO_MM

class B10(FloatEnum):
    WIDTH = 31 / PICA_TO_MM
    HEIGHT = 44 / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
