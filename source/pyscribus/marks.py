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
Classes related to marks management
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.common.xml as xmlc
import pyscribus.exceptions as exceptions

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

mark_type_xml = {
    "anchor": "0",
    "objectref": "1",
    "markref": "2",
    "variable": "3",
    "note": "4",
}

# Classes ===============================================================#

class DocumentMark(xmlc.PyScribusElement):
    """
    Mark element (DOCUMENT/Marks/Mark)
    """

    def __init__(self):
        global mark_type_xml

        super().__init__()

        self.type = ""
        self.name = ""
        self.label = ""

        self.target_object = None
        self.target_mark = {"label": None, "type": "-1"}

        self.pyscribus_defaults = [k for k in mark_type_xml.keys()]

    def fromdefault(self, default):
        """
        :type default: string
        :param default: Set of default settings to apply
        :rtype: boolean
        """

        if default in self.pyscribus_defaults:
            self.type = default

            return True
        else:
            return False

    def set_type(self, mtype):
        """
        :type mtype: string
        :param mtype: Mark type in pyscribus.marks.mark_type_xml keys()
        :rtype: boolean
        :returns: True if setting type succeed
        """
        global mark_type_xml

        if mtype in mark_type_xml.keys():
            self.type = mark_type_xml[mtype]
            return True

        else:
            return False

    def toxml(self):
        """
        :rtype: lxml.etree._Element
        :returns: XML representation of document mark
        """

        global mark_type_xml

        xml = ET.Element("Mark")

        if self.type:

            # --- Label -----------------------------------------------------

            # When @type is "3" (variable text), @str acts as @label
            # in other @types, and @label acts as a mark identifier.
            #
            # So :
            #   DocumentMark.name  = @label if @type == "3"
            #   DocumentMark.label = @label if @type != "3"

            if self.type == "variable":
                xml.attrib["label"] = self.name
            else:
                xml.attrib["label"] = self.label

            # ---------------------------------------------------------------

            xml.attrib["type"] = mark_type_xml[self.type]

            if self.type == "variable":
                xml.attrib["str"] = self.label

            if self.type == "objectref":
                xml.attrib["ItemID"] = self.target_object

            if self.type == "markref":
                xml.attrib["MARKlabel"] = self.target_mark["label"]
                xml.attrib["MARKtype"] = mark_type_xml[self.target_mark["type"]]

        else:
            raise exceptions.InsaneSLAValue("Invalid Marks/Mark @type")

        return xml

    def fromxml(self, xml):
        """
        :rtype: boolean
        :returns: True if XML parsing succeed
        """

        global mark_type_xml

        if xml.tag == "Mark":
            mtype = xml.get("type")

            if mtype is not None:
                for h,x in mark_type_xml.items():
                    if mtype == x:
                        self.type = h
                        break

            # --- Name and/or label -----------------------------------------

            # When @type is "3" (variable text), @str acts as @label
            # in other @types, and @label acts as a mark identifier.
            #
            # So :
            #   DocumentMark.name  = @label if @type == "3"
            #   DocumentMark.label = @label if @type != "3"

            if (mlabel := xml.get("label")) is not None:
                if self.type == "variable":
                    self.name = mlabel
                else:
                    self.label = mlabel

            if self.type == "variable":
                if (mstr := xml.get("str")) is not None:
                    self.label = mstr

            # ---------------------------------------------------------------

            if self.type == "objectref":
                if (mitem := xml.get("ItemID")) is not None:
                    self.target_object = mitem

            if self.type == "markref":
                if (mtarget_label := xml.get("MARKlabel")) is not None:
                    self.target_mark["label"] = mtarget_label

                if (mtarget_type := xml.get("MARKtype")) is not None:

                    if mtarget_type in mark_type_xml.values():
                        self.target_mark["type"] = mark_type_xml[mtarget_type]
                    else:
                        raise exceptions.InsaneSLAValue(
                            "Invalid Marks/Mark @type"
                        )

            return True

        else:
            return False


class StoryMarkAbstract(xmlc.PyScribusElement):
    """
    Abstract class for MARK elements in Scribus stories.

    :type mark_type: str
    :param mark_type: Type of mark
    :type label: str
    :param label: Mark label
    :type features: dict
    :param features: Text formatting features as dict

    .. seealso:: :class:`pyscribus.stories.StoryNoteMark`
    """

    def __init__(self, mark_type, label="", features=False):
        global mark_type_xml

        super().__init__()

        self.features = {
            "inherit": False,
            "superscript": False,
        }

        self.label = label

        if mark_type in mark_type_xml:
            self.type = mark_type
        else:
            raise ValueError("Unknown mark type")

        if features:
            self.set_features(features)

    def fromxml(self, xml):
        global mark_type_xml

        if xml.tag == "MARK":

            if (mtype := xml.get("type")) is not None:
                for h,x in mark_type_xml.items():
                    if mtype == x:
                        self.type = h
                        break

            if (mlabel := xml.get("label")) is not None:
                self.label = mlabel

            if (mfeatures := xml.get("features")) is not None:
                self.set_features(mfeatures)

            return True

        return False

    def toxml(self):
        global mark_type_xml

        xml = ET.Element("MARK")

        xml.attrib["type"] = mark_type_xml[self.type]
        xml.attrib["label"] = self.label

        have_features = len([f for f in self.features.values() if f])

        if have_features:
            features = []

            for f,v in self.features.items():
                if v:
                    features.append(f)

            features = " ".join(features)

            xml.attrib["FEATURES"] = features

        return xml

    def set_features(self, features):
        """
        :type features: str
        :param features: Formatting features as string separated by spaces.
            Ex: ``"inherit superscript"``
        :rtype: bool
        :returns: False if one features was not set.
        """

        features = features.split()

        fset = 0

        for feature in features:
            if feature in self.features.keys():
                self.features[feature] = True
                fset += 1

        if fset == len(features):
            return True
        else:
            return False


class StoryNoteMark(StoryMarkAbstract):
    """
    Mark (MARK) for a (foot|end)note in Scribus stories.
    """

    def __init__(self, label="", features=False):
        StoryMarkAbstract.__init__(self, "note", label, features)

    def fromdefault(self):
        self.set_features("inherit superscript")

    def __repr__(self):
        return "NOTEMARK|{}|{}".format(
            self.label,
            [k for k,v in self.features.items() if self.features[k]]
        )


class StoryVariableMark(StoryMarkAbstract):
    """
    Variable text mark
    """

    def __init__(self, label=""):
        StoryMarkAbstract.__init__(self, "variable", label, False)


class StoryAnchorMark(StoryMarkAbstract):
    """
    Anchor mark
    """

    def __init__(self, label=""):
        StoryMarkAbstract.__init__(self, "anchor", label, False)


class StoryPageObjectRefMark(StoryMarkAbstract):
    """
    Reference to a page object mark
    """

    def __init__(self, label=""):
        StoryMarkAbstract.__init__(self, "objectref", label, False)


class StoryMarkRefMark(StoryMarkAbstract):
    """
    Reference to a mark... mark
    """

    def __init__(self, label=""):
        StoryMarkAbstract.__init__(self, "markref", label, False)

# vim:set shiftwidth=4 softtabstop=4 spl=en:
