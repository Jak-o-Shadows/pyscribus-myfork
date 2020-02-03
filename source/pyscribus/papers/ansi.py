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
ANSI normalized paper sizes.

ANSI A to E formats.

Yes, this is the module for Letter paper sizes, as Letter = ANSI A.
"""

# Imports ===============================================================#

from pyscribus.common.math import FloatEnum, PICA_TO_MM, INCH_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

# NOTE Dimensions are first converted into milimeters
#      because inches makes no sense to my european being.

class Letter(FloatEnum):
    """Letter format. Same as ANSI A."""

    WIDTH = (8.5 * INCH_TO_MM) / PICA_TO_MM
    HEIGHT = (11 * INCH_TO_MM) / PICA_TO_MM

class A(FloatEnum):
    """ANSI A."""

    WIDTH = (8.5 * INCH_TO_MM) / PICA_TO_MM
    HEIGHT = (11 * INCH_TO_MM) / PICA_TO_MM

class B(FloatEnum):
    """ANSI B."""

    WIDTH = (11 * INCH_TO_MM) / PICA_TO_MM
    HEIGHT = (17 * INCH_TO_MM) / PICA_TO_MM

class C(FloatEnum):
    """ANSI C."""

    WIDTH = (17 * INCH_TO_MM) / PICA_TO_MM
    HEIGHT = (22 * INCH_TO_MM) / PICA_TO_MM

class D(FloatEnum):
    """ANSI D."""

    WIDTH = (22 * INCH_TO_MM) / PICA_TO_MM
    HEIGHT = (34 * INCH_TO_MM) / PICA_TO_MM

class E(FloatEnum):
    """ANSI E."""

    WIDTH = (34 * INCH_TO_MM) / PICA_TO_MM
    HEIGHT = (44 * INCH_TO_MM) / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
