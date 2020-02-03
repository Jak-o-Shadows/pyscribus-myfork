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
ISO 269, international system for paper size, additionnal to ISO 216.

C format, including C7/6 and DL.

See iso216paper module for A, B formats.
See iso217paper module for RA, SRA formats.
"""

# Imports ===============================================================#

from pyscribus.common.math import FloatEnum, PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

class C0(FloatEnum):
    WIDTH = 917 / PICA_TO_MM
    HEIGHT = 1297 / PICA_TO_MM

class C1(FloatEnum):
    WIDTH = 648 / PICA_TO_MM
    HEIGHT = 917 / PICA_TO_MM

class C2(FloatEnum):
    WIDTH = 458 / PICA_TO_MM
    HEIGHT = 648 / PICA_TO_MM

class C3(FloatEnum):
    WIDTH = 324 / PICA_TO_MM
    HEIGHT = 458 / PICA_TO_MM

class C4(FloatEnum):
    WIDTH = 229 / PICA_TO_MM
    HEIGHT = 324 / PICA_TO_MM

class C5(FloatEnum):
    WIDTH = 162 / PICA_TO_MM
    HEIGHT = 229 / PICA_TO_MM

class C6(FloatEnum):
    WIDTH = 114 / PICA_TO_MM
    HEIGHT = 162 / PICA_TO_MM

class C76(FloatEnum):
    WIDTH = 81 / PICA_TO_MM
    HEIGHT = 162 / PICA_TO_MM

class C7(FloatEnum):
    WIDTH = 81 / PICA_TO_MM
    HEIGHT = 114 / PICA_TO_MM

class C8(FloatEnum):
    WIDTH = 57 / PICA_TO_MM
    HEIGHT = 81 / PICA_TO_MM

class C9(FloatEnum):
    WIDTH = 40 / PICA_TO_MM
    HEIGHT = 57 / PICA_TO_MM

class C10(FloatEnum):
    WIDTH = 28 / PICA_TO_MM
    HEIGHT = 40 / PICA_TO_MM

class DL(FloatEnum):
    WIDTH = 110 / PICA_TO_MM
    HEIGHT = 220 / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
