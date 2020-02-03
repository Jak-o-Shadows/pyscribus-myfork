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
ISO 217, international system for paper size, additionnal to ISO 216.

Untrimmed paper sizes RA, SRA.

See iso216paper module for A, B formats.
See iso269paper module for C format (including DL).
"""

# Imports ===============================================================#

from pyscribus.common.math import FloatEnum, PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Raw A -----------------------------------------

# 16RA0 3440 × 4880
# 8RA0 2440 × 3440
# 4RA0 1720 × 2440
# 2RA0 1220 × 1720
# RA0 860 × 1220
# RA1 610 × 860
# RA2 430 × 610
# RA3 305 × 430
# RA4 215 × 305

# Supplementary raw A ---------------------------

# 16SRA0 3600 × 5120
# 8SRA0 2560 × 3600
# 4SRA0 1800 × 2560
# 2SRA0 1280 × 1800
# SRA0 900 × 1280
# SRA1 640 × 900
# SRA2 450 × 640
# SRA3 320 × 450
# SRA4 225 × 320

# vim:set shiftwidth=4 softtabstop=4 spl=en:
