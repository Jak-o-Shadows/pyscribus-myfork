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
SLA file.
"""

# Imports ===============================================================#

import re

import lxml
import lxml.etree as ET

import pyscribus.common.xml as xmlc

import pyscribus.exceptions as exceptions
import pyscribus.dimensions as dimensions
import pyscribus.document as document
import pyscribus.stories as stories
import pyscribus.pageobjects as pageobjects

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class SLA(xmlc.PyScribusElement):
    """
    SLA file.

    :type filepath: str
    :param filepath: SLA file path
    :type version: str
    :param version: Scribus version (ex. '1.5.1')
    :type kwargs: dict
    :param kwargs: kwargs

    **Kwargs options :**

    +-----------------------+---------------------------+---------------+
    | Kwarg key             | Use                       | Default value |
    +=======================+===========================+===============+
    | templating            | Use templating ?          | False         |
    +-----------------------+---------------------------+---------------+
    | templatingInsensitive | Should in-text templating | False         |
    |                       | be case insensitive ?     |               |
    +-----------------------+---------------------------+---------------+
    | templatingPattern     | compiled regex to find    | \^%\w+%$      |
    |                       | templated elements        |               |
    |                       | (ex: %TITLE%)             |               |
    +-----------------------+---------------------------+---------------+
    """

    def __init__(self, filepath="", version="", **kwargs):
        super().__init__()

        if version:
            self.version = version.split(".")

        self.document = None

        self.templating = {
            "active": False,
            # In text templating sequences are like %Title%
            "intext-pattern": re.compile('^%\w+%$'),
            # %Title% = %title% = %TITLE% ?
            "intext-insensitive": False,
            # Page object attribute templating names are like %Title%
            "attribute-pattern": re.compile('^%\w+%$'),
            # dict for evaluating an item attribute value as python boolean
            "attribute-eval-bool-keywords": {"true": "True", "false": "False"},
            # Insensitive item attribute value evaluation as boolean ?
            "attribute-eval-bool-insensive": False
        }

        for argname, argvalue in kwargs.items():

            if argname == "templating":
                if argvalue:
                    self.templating["active"] = True

            if argname == "templatingInsensitive":
                if argvalue:
                    self.templating["intext-insensitive"] = True

            if argname == "templatingPattern":

                try:
                    pattern = re.compile(argvalue)
                    self.templating["intext-pattern"] = pattern

                except TypeError:

                    raise TypeError(
                        "templating-pattern must be a re pattern string."
                    )


        if filepath:
            self.parse(filepath, kwargs)

    def fromdefault(self):
        """
        Set default attributes.

        Add a default document.
        """

        doc = document.Document()
        doc.fromdefault()
        self.append(doc)

        return True

    def append(self, sla_object):
        """
        Add the document to SLA Documents and set its sla_parent as self

        :type sla_object: pyscribus.document.Document, other
        :param sla_object: Document or any PyScribus object appendable to a document.
        :type document_index: int
        :param document_index: Index of document if sla_object is not one
        :rtype: boolean
        :returns: True if appending succeed
        """

        if isinstance(sla_object, document.Document):
            sla_object.sla_parent = self
            self.document = sla_object

            return True
        else:
            if self.document is None:
                return False
            else:
                return self.document.append(sla_object)

    def save(self, filepath):
        """
        Save SLA file.

        :type filepath: str
        :param filepath: SLA file path
        :rtype: boolean
        :returns: True if successfull
        """

        xml = self.toxml()

        xml_string = '<?xml version="1.0" encoding="UTF-8"?>' + "\n"
        xml_string += str(
            ET.tostring(
                xml,
                encoding="unicode",
                pretty_print=True
            )
        )

        with open(filepath, "w", encoding="utf8") as slaf:
            slaf.write(xml_string)

    def toxml(self, optional=True):
        """
        Return SLA as lxml.etree._Element

        :type optional: bool
        :param optional: Includes optional attributes (True by default)
        :returns: xml
        :rtype: lxml._Element
        """

        xml = ET.Element("SCRIBUSUTF8NEW")

        xml.attrib["Version"] = ".".join(self.version)

        if self.document is None:
            raise exceptions.InsaneSLAValue(
                "SLA file has no SCRIBUSUTF8NEW/DOCUMENT"
            )
        else:
            dx = self.document.toxml(optional)
            xml.append(dx)

        return xml

    def stories(self, templatable=False):
        """
        Returns all stories from text frames (TextObject) in SLA.

        :param templatable: Only return stories in which there is templatable
            content
        :type templatable: boolean
        :returns: List of pyscribus.story.Story
        :rtype: list
        """

        stories = self.document.stories()

        if templatable:

            if self.templating["active"]:
                return [
                    story for story in stories if story.templatable()
                ]

        return stories

    def pageobjects(self, object_type=False, templatable=False):
        """
        """

        return self.document.pageobjects(object_type, templatable)

    def templatable_stories(self):
        """
        Returns stories from text frames (TextObject) in SLA which contains
        templatable content.
        """

        return self.stories(templatable=True)

    def parse(self, filepath, kwargs):
        """
        Import SLA data from a file path.

        :type filepath: str
        :param filepath: SLA file path
        :type kwargs: dict
        :param kwargs: kwargs
        :returns: True if successfull parsing
        :rtype: boolean
        """

        xml = ET.parse(filepath).getroot()
        success = self.fromxml(xml)

        return success

    def fromxml(self, xml):
        """
        Set SLA content according to <xml> (lxml.etree._Element).

        Use SLA.parse() if you want to import from a file path.

        :returns: True if successfull parsing
        :rtype: boolean

        .. seealso:: pyscribus.sla.SLA.parse()
        """

        def read_xml(obj, xml):
            if xml.tag == "SCRIBUSUTF8NEW":

                if (version := xml.get("Version")) is not None:
                    obj.version = version.split(".")

                for element in xml:

                    if element.tag == "DOCUMENT":
                        doc = document.Document(sla_parent=self)
                        success = doc.fromxml(element)

                        if success:
                            obj.document = doc

                return True, obj

            else:
                return False, obj

        success = False

        if isinstance(xml, lxml.etree._Element):
            success, self = read_xml(self, xml)
        else:
            if os.path.exists(os.path.realpath(xml)):
                xml = lxml.parse(filepath).getroot()
                success, self = read_xml(self, xml)

            else:
                raise TypeError("fromxml requires lxml.etree._Element.")

        return success

# vim:set shiftwidth=4 softtabstop=4 spl=en:
