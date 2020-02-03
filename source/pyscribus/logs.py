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

import logging

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class Logger(logging.Logger):

    def __init__(self):
        super().__init__()

        self.sub_levels = {
            "omitting_pageobjects": logging.INFO
        }

    def setLevel(self, level):
        logging.Logger.setLevel(level)

        for k in self.sub_levels.keys():
            self.sub_levels[k] = level

    def setSubLevel(self, sublevel, level):
        self.sub_levels[sublevel] = level

    def _valid_level(self, la_name, lb):
        if self.sub_levels[la_name] >= lb:
            return True
        else:
            return False

    def debug(self, msg, *args, **kwargs):

        if "logsublevel" in kwargs:

            if self._valid_level(kwargs["logsublevel"], logging.DEBUG):
                logging.Logger.debug(msg, args, kwargs)

        else:
            logging.Logger.debug(msg, args, kwargs)

    def info(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def critical(self, msg, *args, **kwargs):
        pass

# vim:set shiftwidth=4 softtabstop=4 spl=en:
