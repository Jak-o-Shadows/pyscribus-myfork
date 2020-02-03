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
Exceptions raised by PyScribus.
"""

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class InsaneSLAValue(Exception):
    """
    Exception raised if a XML value or a set of XML values is/are
    not possible, are both in contradiction.

    This usually happens if someone edited a SLA file and wroted some
    wrong values in it.

    For example, a list can't be a numeroted and bullet one, Scribus UI
    doesn't allow that but manual SLA editing does.
    """
    pass


class MissingSLAAttribute(Exception):
    """
    Exception raised when a mandatory XML attribute in SLA file is missing.

    An exception more precise than InsaneSLAValue.
    """
    pass


class ConflictingLayer(Exception):
    """
    Exception raised if a document Layer have same attributes that an other one.
    """
    pass

# --- Items attributes -----------------------------------------

class UnknownOrEmptyItemAttributeType(Exception):
    """
    Exception raised when a itemattribute.ItemAttribute (and inherited
    classes) has a unknown or empty type, as it is not in
    itemattribute.ItemAttribute.attrib_types
    """
    pass

# --- Unknown SLA references -----------------------------------

class UnknownLayer(Exception):
    """
    Exception raised if a SLA element points to a layer unknown to the document.
    """
    pass


class UnknownStyleInStory(Exception):
    """
    Exception raised if a SLA element points to a style unknown to the document.
    """
    pass


class InvalidColor(Exception):
    """
    Exception raised when color inks (CMYK or RGB) are invalid, incomplete
    or doesn't even exists.

    RGB inks must range from 0 to 255.
    CMYK inks must range from 0 to 100.
    """
    pass


class UnknownRenderBufferProperty(Exception):
    """
    Exception raised when a render buffer property is missing.
    """
    pass

# --- dimensions -----------------------------------------------

class UnknownDimUnit(Exception):
    pass


class InvalidDim(Exception):
    """
    Exception raised if a dimensions.Dim value is impossible according to its
    unit.

    Pica points must no be inferior to 0.
    (Ordinary) angle (deg unit) must range from 0 to 180.
    Calligraphic pen angle (cdeg unit) must range from 0 to 180.
    """
    pass


class IncompatibleDim(Exception):
    """Exception raised on incompatible dimensions.Dim units conversions."""
    pass

# vim:set shiftwidth=4 softtabstop=4 spl=en:
