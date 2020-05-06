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
Functions for XML <-> Python data conversion.

Most of them are annoyingly simple, but necessary.
"""

# Imports ===============================================================#

import pprint

import copy

import lxml
import lxml.etree as ET

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

num_type_xml = {
    "decimal": "Type_1_2_3",
    "decimal-ar": "Type_1_2_3_ar",
    "lower-roman": "Type_i_ii_iii",
    "upper-roman": "Type_I_II_III",
    "lower-latin": "Type_a_b_c",
    "upper-latin": "Type_A_B_C",
    "alpha-ar": "Type_Alphabet_ar",
    "abjad-ar": "Type_Abjad_ar",
    "hebrew": "Type_Hebrew",
    "asterix": "Type_asterix",
    "cjk": "Type_CJK",
}

alignment = {
    "left": "0",
    "center": "1",
    "right": "2",
    "justify-left": "3",
    "justify": "4"
}

# Classes ===============================================================#

class PyScribusElement:
    """
    Abstract class for any element that must implement PyScribus
    common methods.

    :ivar list pyscribus_defaults: Names of default settings for 
        fromdefault

    .. warning:: except listdefaults, all methods must be redefined by
        inherited classes.
    """

    def __init__(self):
        self.pyscribus_defaults = []

    #--- Quick setup ---------------------------------

    def _quick_setup(self, settings):
        """
        Method for defining style settings from class
        instanciation kwargs.

        In the inherited classes, the redefined method is called
        at class instanciation and PyScribusElement._quick_setup 
        is called in the redefined method.

        Document settings keys in class docstring.

        Only treats "default" setting for inherited classes.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            # Call to fromdefault() to avoid conflicts with later settings

            if "default" in settings:

                if isinstance(settings["default"], bool):
                    self.fromdefault()
                else:
                    self.fromdefault(settings["default"])

    #--- Default(s) ----------------------------------

    def fromdefault(self):
        """
        Modify PyScribus element attributes according to a set of 
        defaults.

        If fromdefault() has not other argument than self, there is
        only one, unnamed, set of default.

        If fromdefault() has a ``default`` argument, there is more
        than one set of default. Use listdefaults() to get the list
        of defaults available.

        :Example:

        .. code:: python

           # The class has only one default
           inherited_class_instance.fromdefault()

           # The class hass more than one default
           inherited_class_instance.fromdefault("english_default")

        """
        pass

    def listdefaults(self):
        """
        List available defaults for the current PyScribus object.

        .. note:: If this method returns an empty list, that
            doesn't mean there is no defaults : it could be mean
            there is **only one** default.

        .. seealso:: fromdefault()

        :rtype: list
        :returns: List of available defaults for fromdefault() method
        """

        return self.pyscribus_defaults

    #--- XML import / export -------------------------

    def toxml(self):
        """
        :rtype: lxml._Element
        :returns: SLA element as LXML ElementTree element
        """

        return False

    def fromxml(self, xml):
        """
        :type xml: lxml._Element
        :param xml: Some XML element
        :rtype: boolean
        :returns: True if XML parsing succeed
        """

        return False

    #--- Copy ----------------------------------------

    def copy(self, **kwargs):
        """
        Returns an independant copy of the instance.

        Use kwargs to quick set this copy as you made it.

        :type kwargs: dict
        :param kwargs: Quick setting (same as __init__)
        """

        duplicate = copy.deepcopy(self)

        if kwargs:
            duplicate._quick_setup(kwargs)

        return duplicate


class OrphanElement(PyScribusElement):
    """
    Abstract class for any element that must implement PyScribus
    common method and don't have any XML attribute & child.

    :type tag: str
    :param tag: XML tag

    :ivar string tag: XML tag
    """

    def __init__(self, tag):
        PyScribusElement.__init__(self)
        self.tag = tag

    def toxml(self):
        """
        :rtype: lxml._Element
        """
        xml = ET.Element(self.tag)
        return xml

    def fromdefault(self):
        # NOTE As this class implements XML elements without any attribute
        # or childs possible, an instanciation of OrphanElement is already
        # a default.
        return True

    def fromxml(self, xml):
        """
        Parse XML element with tag OrphanElement.tag

        :param xml: XML element
        :type xml: lxml._Element
        :rtype: bool
        :returns: bool
        """
        if xml.tag == self.tag:
            return True

        return False

    def __str__(self):
        return "<{}/>".format(self.tag)

# Fonctions =============================================================#

# We need a better typology of functions here :
#
# +---------------------+------------------+---------+---------------------------------+-----------+
# | Function name       | New name ?       | Returns | Manipulation                    | Side      |
# +---------------------+------------------+---------+---------------------------------+-----------+
# | float_or_int_string | out_cleanfloat   | string  | number without useless decimals | xml       |
# | str_or_nonestr      | out_str_nonestr  | string  | string or "None"                | xml ?     |
# | bool_to_num         | out_num_boolean  | string  | boolean as "0" or "1"           | xml       |
# | num_to_bool         | in_num_boolean   | boolean | "0" or "1" as boolean           | pyscribus |
# | bool_or_else_to_num | out_zero_string  | string  | "0" if not(v) or v              | xml       |
# | none_or_str         | out_empty_string | string  | "" if v is None or v            | xml ?     |
# +---------------------+------------------+---------+---------------------------------+-----------+

def float_or_int_string(f):

    if float(f) == int(f):
        return str(int(f))
    else:
        return str(f)

def str_or_nonestr(v):
    """
    Returns v if v is a non-empty string, else returns 'None'.

    :rtype: str
    """

    if v:
        return v
    else:
        return "None"

def bool_to_num(b):
    """
    Returns '1' if b is true, returns '0' if b is false.

    :rtype: str
    """

    if b:
        return "1"
    else:
        return "0"

def num_to_bool(n):
    """
    Return True if n == '1', else returns False.

    :rtype: bool
    """

    if n == "1":
        return True
    else:
        return False

def bool_or_else_to_num(b):
    """
    Returns '0' if b is False, else return b as string.

    :rtype: str
    """

    if b:
        return str(b)
    else:
        return "0"

def none_or_str(v):
    """
    If v is None, return empty string, else return v as string.

    :rtype: str
    """
    if v is None:
        return ""
    else:
        return str(v)

def undocumented_to_python(xml, attributes):
    """
    Function to manage the import of undocumented
    XML/SLA attributes.

    Used in PyScribus fromxml() methods until there is
    no attribute undocumented and handled.

    :param xml: XML element
    :type xml: lxml._Element
    :param attributes: List of attributes' names
    :type attributes: list
    :returns: Dictionnary with attributes names as 
        keys and attribute values as values.
    :rtype: dict

    Use lxml._Element.get() to get attributes values,
    so missing attributes will have None as a value.

    .. seealso:: `undocumented_to_xml()`
    """
    undocumented = {}

    for att_name in attributes:
        undocumented[att_name] = xml.get(att_name)

    return undocumented

def undocumented_to_xml(xml, undocumented, no_none=False):
    """
    Function to manage the export of undocumented
    XML/SLA attributes.

    Used in PyScribus toxml() methods until there is
    no attribute undocumented and handled.

    :param xml: XML element
    :type xml: lxml._Element
    :param undocumented: Dictionnary of XML attributes.
        Return of undocumented_to_python()
    :type undocumented: dict
    :returns: xml
    :rtype: lxml._Element

    Add attributes to a XML element using undocumented
    dictionnary keys as XML attributes' names and
    undocumented dictionnary values as XML attributes'
    values.

    None values are ignored, through none_or_str().

    .. seealso:: undocumented_to_python()
    """

    for undatt, undvalue in undocumented.items():
        if no_none:
            if undvalue is None:
                continue

        xml.attrib[undatt] = none_or_str(undvalue)

    return xml

def all_undocumented_to_python(xml):
    """
    Function to manage the import of undocumented
    XML/SLA attributes.

    Used in PyScribus fromxml() methods until there is
    no attribute undocumented and handled.

    Used instead of undocumented_to_python() if there
    is no defined list of undocumented attributes.

    :param xml: XML element
    :type xml: lxml._Element
    :param attributes: List of attributes' names
    :type attributes: list
    :returns: Dictionnary with attributes names as
        keys and attribute values as values.
    :rtype: dict

    Get all xml attributes names and values so that
    all_undocumented_to_xml() will only have to filter
    those which aren't already in the LXML element to
    export.

    .. seealso:: all_undocumented_to_xml()
    """
    undocumented = {}

    for att_name, att_value in xml.attrib.items():
        undocumented[att_name] = att_value

    return undocumented

def all_undocumented_to_xml(xml, undocumented, report=True, msg=""):
    """
    Function to manage the export of undocumented
    XML/SLA attributes.

    Used in PyScribus toxml() methods until there is
    no attribute undocumented and handled.

    :param xml: XML element
    :type xml: lxml._Element
    :param undocumented: Dictionnary of XML attributes.
        Return of all_undocumented_to_python()
    :type undocumented: dict
    :returns: List containing LXML element and undocumented attributes
        names list.
    :rtype: list

    Only adds undocumented attributes to xml element if
    xml element doesn't already have this attribute.

    .. seealso:: all_undocumented_to_python()
    """

    undoc_attribs = []

    for att_name, att_value in undocumented.items():

        if att_name not in xml.attrib:
            xml.attrib[att_name] = att_value
            undoc_attribs.append(att_name)

    if report and undoc_attribs:
        print("Undocumented XML attributes in {} :".format(msg))
        pprint.pprint(undoc_attribs, width=80, compact=True)

    return [xml, undoc_attribs]

# vim:set shiftwidth=4 softtabstop=4 spl=en:
