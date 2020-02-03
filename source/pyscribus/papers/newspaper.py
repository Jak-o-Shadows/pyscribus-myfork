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

from pyscribus.common.math import PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

BERLINER_WIDTH = 320 / PICA_TO_MM
BERLINER_HEIGHT = 470 / PICA_TO_MM

BROADSHEET_WIDTH = 410 / PICA_TO_MM
BROADSHEET_HEIGHT = 575 / PICA_TO_MM

BELGIAN_WIDTH = 365 / PICA_TO_MM
BELGIAN_HEIGHT = 520 / PICA_TO_MM

BELGIAN_50_WIDTH = 370 / PICA_TO_MM
BELGIAN_50_HEIGHT = 500 / PICA_TO_MM

TABLOID_WIDTH = 290 / PICA_TO_MM
TABLOID_HEIGHT = 410 / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
