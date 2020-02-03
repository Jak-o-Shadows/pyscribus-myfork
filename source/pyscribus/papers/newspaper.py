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
Often used newspapers sizes.

Berliner, Belgian, Tabloid, Broadsheet formats.
"""

# Imports ===============================================================#

from pyscribus.common.math import FloatEnum, PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

class Berliner(FloatEnum):
    WIDTH = 320 / PICA_TO_MM
    HEIGHT = 470 / PICA_TO_MM

class Broadsheet(FloatEnum):
    WIDTH = 410 / PICA_TO_MM
    HEIGHT = 575 / PICA_TO_MM

class Belgian(FloatEnum):
    WIDTH = 365 / PICA_TO_MM
    HEIGHT = 520 / PICA_TO_MM

class Belgian50(FloatEnum):
    WIDTH = 370 / PICA_TO_MM
    HEIGHT = 500 / PICA_TO_MM

class Tabloid(FloatEnum):
    WIDTH = 290 / PICA_TO_MM
    HEIGHT = 410 / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
