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
PyScribus classes for notes
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions

from pyscribus.common.xml import *

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class Note(PyScribusElement):
    """
    Note element (Note)
    """

    def __init__(self):
        PyScribusElement.__init__(self)

        self.style = ""
        self.parent_mark = ""
        self.parent_frame = ""
        self.text = NoteText()

    def fromdefault(self):
        self.style = "Default"
        self.text = NoteText()
        self.text.fromdefault()

    def get_parent_mark(self):
        return "NoteMark_{} in frame {}".format(
            self.style, self.parent_frame
        )

    def fromxml(self, xml):

        if xml.tag == "Note":
            style = xml.get("NStyle")
            parent_mark = xml.get("Master")

            if style is not None:
                self.style = style

            if parent_mark is not None:
                self.parent_mark = parent_mark
                self.parent_frame = self.parent_mark.split("in frame ")[-1]

            if "Text" in xml.attrib:
                text = NoteText()
                success = text.fromxml(xml)

                if success:
                    self.text = text

            return True
        else:
            return False

    def toxml(self):
        xml = ET.Element("Note")

        xml.attrib["Master"] = self.get_parent_mark()
        xml.attrib["NStyle"] = self.style
        xml.attrib["Text"] = self.text.toxmlstr()

        return xml


class NoteText(PyScribusElement):
    """
    Note element text (Note/@Text).

    Note element text consists in a full XML file dumped into 
    @Text attribute of Note, hence the need for a specific 
    class.
    """

    #Text="&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;&lt;SCRIBUSTEXT &gt;&lt;defaultstyle /&gt;&lt;p &gt;&lt;style /&gt;&lt;span &gt;&lt;charstyle Features=&quot;inherit &quot; /&gt; Pri tiuj ĉi ideoj « estas modo » paroli ne alie, ol kun ironia kaj malestima rideto, tial tiel agas ankaŭ A kaj B kaj C, kaj ĉiu el ili timas enpensiĝi serioze eĉ unu minuton pri la mokata ideo, ĉar li « scias antaŭe », ke « ĝi krom malsaĝaĵo enhavas ja nenion », kaj li timas, ke oni iel alkalkulos lin mem al la nombro de « tiuj malsaĝuloj », se li eĉ en la daŭro de unu minuto provos rilati serioze al tiu ĉi malsaĝaĵo. La homoj miras, « kiamaniere en nia praktika tempo povas aperi tiaj malsaĝaj fantaziuloj kaj kial oni ne metas ilin en la domojn por frenezuloj ».&lt;/span&gt;&lt;/p&gt;&lt;/SCRIBUSTEXT&gt;&#10;"/>

    #Text="
    # <?xml version="1.0" encoding="UTF-8"?>
    # <SCRIBUSTEXT >
        # <defaultstyle />
        # <p >
            # <style />
            # <span >
                # <charstyle Features="inherit " />
                # Pri tiuj ĉi ideoj « estas modo » paroli ne alie, ol kun ironia kaj malestima rideto, tial tiel agas ankaŭ A kaj B kaj C, kaj ĉiu el ili timas enpensiĝi serioze eĉ unu minuton pri la mokata ideo, ĉar li « scias antaŭe », ke « ĝi krom malsaĝaĵo enhavas ja nenion », kaj li timas, ke oni iel alkalkulos lin mem al la nombro de « tiuj malsaĝuloj », se li eĉ en la daŭro de unu minuto provos rilati serioze al tiu ĉi malsaĝaĵo. La homoj miras, « kiamaniere en nia praktika tempo povas aperi tiaj malsaĝaj fantaziuloj kaj kial oni ne metas ilin en la domojn por frenezuloj ».
            # </span>
        # </p>
    # </SCRIBUSTEXT>
    # &#10;"/>

    def __init__(self):
        PyScribusElement.__init__(self)

    def fromxml(self, xml):

        if xml == "Note":
            content = xml.get("Text")

            if content is not None:
                text = content

                # &#10; = Line feed character

                for normalise in [
                            [" &gt;&lt;","><"], ["&lt;", "<"], ["&gt;", ">"],
                            ["&quot;", '"'], ["&#10;",""]
                        ]:
                    text = text.replace(normalise[0], normalise[1])

                xml_text = ET.fromstring(text)

                return True
            else:
                return False
        else:
            return False

    def toxml(self):
        """
        Alias of toxmlstr()
        """
        return self.toxmlstr()

    def toxmlstr(self):
        xml_string = ""

        # TODO

        return xml_string


class NoteFrame(PyScribusElement):
    """
    Note frame (NotesFrames/FOOTNOTEFRAME).
    """

    def __init__(self):
        PyScribusElement.__init__(self)

        # NOTE @myID
        # The page object where the note content is located
        self.own_frame_id = None

        # NOTE @MasterID
        # The page object with the story where note references are located
        self.story_frame_id = None

        # NOTE @NSname
        self.note_style = None

    def fromxml(self, xml):

        if xml == "FOOTNOTEFRAME":
            note_style = xml.get("NSname")
            own_frame = xml.get("myID")
            story_frame = xml.get("MasterID")

            if note_style is not None:
                self.note_style = note_style

            if own_frame is not None:
                self.own_frame_id = own_frame

            if story_frame is not None:
                self.story_frame_id = story_frame

            if story_frame is None or own_frame is None:

                raise exceptions.InsaneSLAValue(
                    "Note frame has no page object ID or\
                     no parent page object ID."
                )

            return True

        return False

    def toxml(self):
        xml = ET.Element("FOOTNOTEFRAME")

        if self.note_style is not None:
            xml.attrib["NSname"] = self.note_style

        if self.own_frame_id is not None:
            xml.attrib["myID"] = self.own_frame_id

        if self.story_frame_id is not None:
            xml.attrib["MasterID"] = self.story_frame_id

        return xml

    def fromdefault(self):
        self.note_style = "Default"

# vim:set shiftwidth=4 softtabstop=4 spl=en:
