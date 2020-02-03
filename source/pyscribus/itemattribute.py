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
Item attributes for document, page objects.
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions

from pyscribus.common.xml import *

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class ItemAttribute(PyScribusElement):
    attrib_types = ["boolean", "integer", "double", "string", "none"]

    #--- FIXME Not documented -----------------------------
    # Parameter=""
    # Relationship="none"
    # RelationshipTo=""
    # AutoAddTo="none"

    #--- NOTE Examples in SLA -----------------------------
    # Name="entier" Type="integer" Value="1"
    # Name="reel" Type="double" Value="-5"
    # Name="chaine" Type="string" Value="&quot;Test&quot;"
    # Name="" Type="none" Value=""

    def __init__(self):
        super().__init__()

        self.name = ""
        self.attribute_type = "none"
        self.value = ""

    def as_python(
            self, bool_keywords={"true": "True", "false": "False"},
            lower_bool=False):
        """
        Returns the value of ItemAttribute.value as a valid python
        object (int for integer, bool for boolean, etc).

        :type bool_keywords: dict
        :param bool_keywords: Dictionnary of true and false values to test
            against. If bool_keywords["true"] is equal to
            ItemAttribute.value (as a string), True is returned, otherwise
            False is returned. Example : {"true": "1", "false": "0"}
        :type lower_bool: boolean
        :param lower_bool: In the case of boolean ItemAttribute type, it may
            be useful to switch ItemAttribute.value as a lowercase string to
            avoid case issues with bool_keywords.

        Returns :

        - int object if attribute type is "integer"
        - float object if attribute type is "double"
        - str object if attribute type is "string"
        - bool object if attribute type is "boolean"
        - str if attribute_type is "none", as attribute_type "none" allows
            other values than None.

        Raise a ValueError if attribute_type is empty/unknown.

        :rtype: int,long,string,boolean
        """

        if self.attribute_type == "integer":
            return int(self.value)
        elif self.attribute_type == "double":
            return float(self.value)
        elif self.attribute_type == "string":
            # FIXME TODO Escape &quot; and other entities in unicode caracters
            return str(self.value)
        elif self.attribute_type == "none":
            return self.value
        elif self.attribute_type == "boolean":
            if lower_bool:
                v = str(self.value).lower()
            else:
                v = str(self.value)

            if v == bool_keywords["true"]:
                return True
            else:
                return False
        else:
            raise exceptions.UnknownOrEmptyItemAttributeType()

    #--- PyScribus standard methods ----------------------------

    def fromxml(self, xml):
        name = xml.get("Name")

        if name is not None:
            self.name = name

        atype = xml.get("Type")

        if atype is not None:
            if atype.lower() in ItemAttribute.attrib_types:
                self.attribute_type = atype.lower()

        v = xml.get("Value")

        if v is not None:
            self.value = v

        # TODO

        return True

    def toxml(self):
        xml = ET.Element("ItemAttribute")

        xml.attrib["Name"] = self.name
        xml.attrib["Type"] = self.attribute_type
        xml.attrib["Value"] = self.value

        # TODO

        return xml

    def fromdefault(self):
        # TODO

        self.attribute_type = "none"


class DocumentAttribute(ItemAttribute):
    """
    Item attribute at document level
    """

    def __init__(self):
        super().__init__()


class PageObjectAttribute(ItemAttribute):
    """
    Item attribute at page object level
    """

    def __init__(self):
        super().__init__()

# vim:set shiftwidth=4 softtabstop=4 spl=en:
