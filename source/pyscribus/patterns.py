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
PyScribus classes for patterns.
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions
import pyscribus.dimensions as dimensions
import pyscribus.pageobjects as pageobjects

from pyscribus.common.xml import *

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class Pattern(PyScribusElement):
    """
    Pattern in SLA (Pattern)

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    # <Pattern
    #     xoffset="0"
    #     yoffset="0"
    # >

    def __init__(self, sla_parent=False, doc_parent=False):
        super().__init__()

        self.name = None

        self.items = []

        self.sla_parent = sla_parent
        self.doc_parent = doc_parent

        # NOTE We do not set a dimensions.DimBox because patterns is not meant
        # to be used directly on the page

        self.dims = {
            "width": None,
            "height": None
        }

        self.scale = {
            "x": None,
            "y": None
        }

    def fromxml(self, xml):
        """
        """

        if xml.tag == "Pattern":

            if (name := xml.get("Name")) is not None:
                self.name = name

            for dim in ["width", "height"]:

                if (att := xml.get(dim)) is not None:
                    self.dims[dim] = dimensions.Dim(float(att))

            for scale in ["x", "x"]:
                att_name = "scale{}".format(scale.upper())

                if (att := xml.get(att_name)) is not None:
                    self.scale[scale] = dimensions.Dim(float(att), "pcdecim")

            # TODO FIXME xoffset yoffset

            for element in xml:

                if element.tag == "PatternItem":
                    pie = PatternItem(self.sla_parent, self.doc_parent)

                    if (success := pie.fromxml(element)):
                        self.items.append(pie)

            return True

        return False

    def toxml(self):
        """
        """

        xml = ET.Element("Pattern")

        if self.name is not None:
            xml.attrib["Name"] = self.name

        for dim in ["width", "height"]:
            if self.dims[dim] is None:
                raise ValueError(
                    "Pattern {} must have a(n) {}.".format(
                        self.name, dim
                    )
                )
            else:
                xml.attrib[dim] = self.dims[dim].toxmlstr()

        for scale in ["x", "y"]:
            att_name = "scale{}".format(scale.upper())

            if self.scale[scale] is None:
                xml.attrib[att_name] = "1"
            else:
                xml.attrib[att_name] = self.scale[scale].toxmlstr()

        # TODO FIXME xoffset yoffset

        for item in self.items:
            ix = item.toxml()
            xml.append(ix)

        return xml


class PatternItem(pageobjects.PageObject):
    """
    Pattern item in SLA (Pattern/PatternItem)

    (Pattern items are encoded as polygon page objects with a different XML tag)

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    # <PatternItem XPOS="0.187499995780351" YPOS="0.187499995780351" OwnPage="-1" ItemID="204434288" PTYPE="6" WIDTH="6.55552657556513" HEIGHT="4.82126570393049" FRTYPE="3" CLIPEDIT="1" PWIDTH="0.374999991560701" PCOLOR="FromSVG#de4344" PCOLOR2="FromSVG#de4344" PLINEART="1" PLINEJOIN="128" ANNAME=" path861" TEXTFLOWMODE="1" path="M3.6e-7 4.44089e-16 L6.55553 2.41063 L0 4.82127 C1.0473 3.39803 1.04126 1.45079 3.6e-7 0 L3.6e-7 4.44089e-16 Z" copath="M3.6e-7 4.44089e-16 L6.55553 2.41063 L0 4.82127 C1.0473 3.39803 1.04126 1.45079 3.6e-7 0 L3.6e-7 4.44089e-16 Z" gXpos="0.187499995780351" gYpos="0.187499995780351" gWidth="6.93052656712583" gHeight="5.19626569549119" LAYER="0"/>

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        pageobjects.PageObject.__init__(self, "polygon", sla_parent, doc_parent)
        pageobjects.PageObject._quick_setup(self, kwargs)

    def fromxml(self, xml):
        """
        """

        success = pageobjects.PageObject.fromxml(
            self, xml, arbitrary_tag="PatternItem"
        )

        return success

    def toxml(self):
        """
        """

        xml = pageobjects.PageObject.toxml(arbitrary_tag="PatternItem")

        return xml

# vim:set shiftwidth=4 softtabstop=4 spl=en:
