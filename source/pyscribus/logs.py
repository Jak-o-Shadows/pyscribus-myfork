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
Logging for PyScribus
"""

# Imports ===============================================================#

import os
import logging

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

USE_LOG = False

# Fonctions =============================================================#

def init_logging(
        filepath="test.log",
        formatstr="%(asctime)s:%(levelname)s:%(message)s"):
    global USE_LOG

    logger = getLogger()

    filepath = os.path.realpath(filepath)

    logging.basicConfig(
        filename=filepath,
        level=logging.DEBUG,
        format=formatstr
    )

    USE_LOG = True

def getLogger():
    global USE_LOG

    if USE_LOG:
        return logging.getLogger('pyscribus')
    else:
        return False

# vim:set shiftwidth=4 softtabstop=4 spl=en:
