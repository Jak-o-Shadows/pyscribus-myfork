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
Classes of PyScribus related to table of contents & sections
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.common.xml as xmlc

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class Section(xmlc.PyScribusElement):
    """
    Section in SLA (Section).
    """

    def __init__(self):
        super().__init__()

        self.active = False
        self.reversed = False

        self.name = ""
        self.number = 1

        self.range = {"from": 0, "to": 0}

        self.numerotation = {
            "type": "decimal",
            "start": 1
        }

        self.fill = {
            "width": 0,
            "character": chr(0)
        }

    def fromdefault(self):
        """
        Set default attributes for the section.
        """

        self.active = True
        self.reversed = False

        self.name = "0"
        self.number = 1

        self.range = {"from": 0, "to": 0}

        self.numerotation = {
            "type": "decimal",
            "start": 1
        }

        self.fill = {
            "width": 0,
            "character": chr(0)
        }

    def fromxml(self, xml):
        """
        :rtype: boolean
        :returns: True if parsing succeed
        """

        if xml.tag == "Section":

            nam = xml.get("Name")

            if nam is not None:
                self.name = nam

            #------------------------------------------------------

            rev = xml.get("Reversed")
            act = xml.get("Active")

            if rev is not None:
                self.reversed = xmlc.num_to_bool(rev)

            if act is not None:
                self.active = xmlc.num_to_bool(act)

            #--- Section number -----------------------------------

            num = xml.get("Number")

            if num is not None:
                self.number = int(num) + 1

            #--- Page range ---------------------------------------

            for case in [["From", "from"], ["To", "to"]]:
                att = xml.get(case[0])

                if att is not None:
                    self.range[case[1]] = int(att) + 1

            #--- Numerotation -------------------------------------

            num_type = xml.get("Type")

            if num_type is not None:

                for human,code in xmlc.num_type_xml.items():

                    if code == num_type:

                        self.numerotation["type"] = human
                        break

            num_start = xml.get("Start")

            if num_start is not None:
                self.numerotation["start"] = int(num_start)

            #--- Filling ------------------------------------------

            fill_char = xml.get("FillChar")

            if fill_char is not None:

                try:
                    self.fill["character"] = chr(int(fill_char))

                except ValueError:
                    # NOTE Because python chr() argument must be in 
                    #      [0-1114111] range

                    raise exceptions.InsaneSLAValue(
                        "Fill character in section '{}' "\
                        "must range from 0 to 1114111.".format(
                            self.name
                        )
                    )

            field_width = xml.get("FieldWidth")

            if field_width is not None:
                self.fill["width"] = int(field_width)

            #------------------------------------------------------

            return True
        else:
            return False

    def toxml(self):
        """
        :rtype: lxml.etree._Element
        :returns: XML representation of section
        """
        xml = ET.Element("Section")

        xml.attrib["Number"] = str(self.number - 1)
        xml.attrib["Name"] = self.name
        xml.attrib["From"] = str(self.range["from"] - 1)
        xml.attrib["To"] = str(self.range["to"] - 1)
        xml.attrib["Type"] = xmlc.num_type_xml[self.numerotation["type"]]
        xml.attrib["Start"] = str(self.numerotation["start"])
        xml.attrib["Reversed"] = xmlc.bool_to_num(self.reversed)
        xml.attrib["Active"] = xmlc.bool_to_num(self.active)
        xml.attrib["FillChar"] = str(ord(self.fill["character"]))

        # TODO Understanding what FieldWidth argument really means
        xml.attrib["FieldWidth"] = str(self.fill["width"])

        return xml


class TOC(xmlc.PyScribusElement):
    """
    Table of content element in SLA (TablesOfContents/TableOfContents)
    """

    placement_to_xml = {
        "end": "End",
        "start": "Beginning",
        "hidden": "NotShown",
    }

    def __init__(self):
        super().__init__()

        self.name = ""
        self.frame_name = ""
        self.attribute = ""
        self.non_printing = False
        self.style = ""
        self.placement = "end"

    def fromdefault(self):
        self.name = "Table of contents"
        self.placement = "end"
        self.non_printing = False

    def toxml(self):
        toc = ET.Element("TableOfContents")

        toc.attrib["Name"] = self.name
        toc.attrib["ItemAttributeName"] = xmlc.str_or_nonestr(self.attribute)
        toc.attrib["FrameName"] = self.frame_name
        toc.attrib["ListNonPrinting"] = xmlc.bool_to_num(self.non_printing)
        toc.attrib["Style"] = self.style
        toc.attrib["NumberPlacement"] = TOC.placement_to_xml[self.placement]

        return toc

    def fromxml(self, xml):
        """
        :rtype: boolean
        :returns: True if parsing succeed
        """

        if xml.tag == "TableOfContents":

            if (nam := xml.get("Name")) is not None:
                self.name = nam

            if (fnam := xml.get("FrameName")) is not None:
                self.frame_name = fnam

            if (sn := xml.get("Style")) is not None:
                self.style = sn

            if (np := xml.get("ListNonPrinting")) is not None:
                self.non_printing = xmlc.num_to_bool(np)

            #--------------------------------------------------------

            if (fattribute := xml.get("ItemAttributeName")) is not None:

                if fattribute == "None":
                    self.attribute = ""
                else:
                    self.attribute = fattribute

            #--------------------------------------------------------

            if (placement := xml.get("NumberPlacement")) is not None:

                for human, code in TOC.placement_to_xml.items():

                    if placement == code:
                        self.placement = human
                        break

            #--------------------------------------------------------

            return True

        else:
            return False

# vim:set shiftwidth=4 softtabstop=4 spl=en:
