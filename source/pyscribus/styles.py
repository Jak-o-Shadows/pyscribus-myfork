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
PyScribus classes for styles manipulation.
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.common.xml as xmlc
import pyscribus.exceptions as exceptions
import pyscribus.dimensions as dimensions

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class NoteStyle(xmlc.PyScribusElement):
    """SLA notes style (notesStyle)"""

    range_type_xml = {
        "document": "0", "section": "1",
        "story": "2", "page": "3",
        "form": "4"
    }

    def __init__(self, default=False):
        super().__init__()

        if default:
            self.fromdefault()
        else:
            self.name = ""
            self.set_type("footnote")
            self.num_start = 1
            self.num_type = "decimal"
            self.affixes = {"prefix": "", "suffix": ""}
            self.auto_dims = {"width": True, "height": True}
            self.auto_remove = True
            self.auto_link = True
            self.superscript = {"note": True, "mark": True}
            self.styles = {"mark": "", "note": ""}
            self.range = "document"

    def set_numtype(self, numtype):
        if numtype.lower() in NoteStyle.keys():
            self.num_type = numtype.lower()
            return True
        else:
            return False

    def set_type(self,note_type="footnote"):
        if note_type.lower() == "footnote":
            self.is_endnotes = False
            self.is_footnotes = True
        else:
            self.is_endnotes = True
            self.is_footnotes = False

    def toxml(self):
        xml = ET.Element("notesStyle")

        xml.attrib["Name"] = self.name
        xml.attrib["Start"] = str(self.num_start)
        xml.attrib["Endnotes"] = xmlc.bool_to_num(self.is_endnotes)
        # xml.attrib["Type"] = NoteStyle.num_type_xml[self.num_type]
        xml.attrib["Type"] = xmlc.num_type_xml[self.num_type]
        xml.attrib["Range"] = NoteStyle.range_type_xml[self.range]
        xml.attrib["Prefix"] = self.affixes["prefix"]
        xml.attrib["Suffix"] = self.affixes["suffix"]
        xml.attrib["AutoHeight"] = xmlc.bool_to_num(self.auto_dims["height"])
        xml.attrib["AutoWidth"] = xmlc.bool_to_num(self.auto_dims["width"])
        xml.attrib["AutoRemove"] = xmlc.bool_to_num(self.auto_remove)
        xml.attrib["AutoWeld"] = xmlc.bool_to_num(self.auto_link)
        xml.attrib["SuperNote"] = xmlc.bool_to_num(self.superscript["note"])
        xml.attrib["SuperMaster"] = xmlc.bool_to_num(self.superscript["mark"])
        xml.attrib["MarksStyle"] = self.styles["mark"]
        xml.attrib["NotesStyle"] = self.styles["note"]

        return xml

    def fromxml(self, xml):
        self.num_start = int(xml.get("Start"))
        self.name = xml.get("Name")
        self.affixes["prefix"] = xml.get("Prefix")
        self.affixes["suffix"] = xml.get("Suffix")
        self.auto_link = xmlc.num_to_bool(xml.get("AutoWeld"))
        self.auto_remove = xmlc.num_to_bool(xml.get("AutoRemove"))
        self.auto_dims["width"] = xml.get("AutoWidth")
        self.auto_dims["height"] = xml.get("AutoHeight")
        self.superscript["note"] = xmlc.num_to_bool(xml.get("SuperNote"))
        self.superscript["mark"] = xmlc.num_to_bool(xml.get("SuperMaster"))
        self.styles["note"] = xml.get("NotesStyle")
        self.styles["mark"] = xml.get("MarksStyle")

        nt = xml.get("Type")

        # for h,x in NoteStyle.num_type_xml.items():
        for h,x in xmlc.num_type_xml.items():
            if nt == x:
                self.num_type = h
                break

        rg = xml.get("Range")

        for h,x in NoteStyle.range_type_xml.items():
            if rg == x:
                self.range = h
                break

        return True

    def fromdefault(self):
        self.name = "Default"
        self.set_type("footnote")
        self.num_start = 1
        self.num_type = "decimal"
        self.affixes = {"prefix": "", "suffix": ")"}
        self.auto_dims = {"width": True, "height": True}
        self.auto_remove = True
        self.auto_link = True
        self.superscript = {"note": True, "mark": True}
        self.styles = {"mark": "", "note": ""}
        self.range = "document"

        return True

# FIXME This is a giant class.
# When styles attributes list will be stable, we will need to :
#   - move the type-specific (to|from)xml code and class attributes to
#     inherited classes. StyleAbstract.toxml() already returns xml Element.
#   - move the type-specific functions to inherited classes

class StyleAbstract(xmlc.PyScribusElement):
    """
    Abstract class for paragraph, character, table, cell styles in SLA.

    :type style_type: str
    :param style_type: Style type. Must be "paragraph", "character", 
        "table", "cell".
    :type default: boolean
    :param default: Use default settings (False by default)
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs tables of inherited classes)
    """

    # TODO Reste des attributs

    type_xml = {
        "paragraph": "STYLE", "character": "CHARSTYLE",
        "table": "TableStyle", "cell": "CellStyle"
    }

    name_xml = {
        "NAME": ["paragraph", "table", "cell"],
        "CNAME": ["character"]
    }

    shortcut_xml = {
        "PSHORTCUT": ["paragraph"],
        "SHORTCUT": ["character"]
    }

    parent_xml = {
        "PARENT": ["paragraph"],
        "CPARENT": ["character"]
    }

    fshade_xml = {
        "FillShade": ["table", "cell"],
        "FSHADE": ["character", "paragraph"]
    }

    fcolor_xml = {
        "FillColor": ["table", "cell"],
        "FCOLOR": ["character", "paragraph"]
    }

    default_name = {
        "paragraph": "Default Paragraph Style",
        "character": "Default Character Style",
        "table": "Default Table Style",
        "cell": "Default Cell Style"
    }

    default_font = {
        "name": "Arial Regular",
        "size": 12,
        "features": [],
        "color": "Black",
        "alignment": "left"
    }

    def __init__(self, style_type, doc_parent, default=False, **kwargs):
        super().__init__()

        self.doc_parent = doc_parent

        if not style_type.lower() in StyleAbstract.type_xml.keys():
            raise ValueError("Unknown style type for StyleAbstract")

        self.style_type = style_type.lower()

        self.name = ""
        self.parent = None

        self.is_default = False

        if self.style_type in ["paragraph", "character"]:
            # TODO FIXME Handle font features as a dict instead
            # of a list, like in other styles
            # Features: -clig, inherit

            self.font = {
                "name": "",
                "size": 0,
                "features": [],
                "color": "",
                "alignment": "left"
            }

            # NOTE Weird, but FONTFEATURES is not the same as FEATURES
            # even if it has obviously an effect on fonts...
            self.features = {
            }

            self.lang = None
            self.shortcut = None

        if self.style_type in ["table", "cell", "character", "paragraph"]:
            self.fill = {
                "color": None,
                "shade": None
            }

        if self.style_type in ["table", "cell"]:
            self.borders = []

        if self.style_type == "character":
            self.scale = {
                "horizontal": 100,
                "vertical": 100
            }

        if self.style_type == "cell":
            self.padding = {
                "left": 0, "right": 0,
                "top": 0, "bottom": 0
            }

        if self.style_type == "paragraph":
            self.tabs = []
            self.character_parent = ""

            self.space = {
                "after": None,
                "before": None,
            }

            self.leading = {
                "mode": None,
                "value": dimensions.Dim(0)
            }

        if default:
            self.fromdefault()

        if kwargs:
            self._quick_setup(kwargs)

    def _quick_setup(self, settings):
        """
        Method for defining style settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            xmlc.PyScribusElement._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                if self.style_type in ["paragraph", "character"]:

                    if setting_name == "defaultstyle":
                        if setting_value:
                            self.is_default = True
                        else:
                            self.is_default = False

                if setting_name == "name":
                    self.name = setting_value

                if setting_name == "parent":
                    self.parent = setting_value

                if self.style_type in ["paragraph", "character"]:

                    if setting_name == "fontsize":
                        self.font["size"] = setting_value

                    if setting_name == "font":
                        self.font["name"] = setting_value

    def _choose_att(self, atts_dict):
        """
        Returns the correct XML attribute according to the
        StyleAbstract *class* attribute atts_dict.
        """
        for att, types in atts_dict.items():
            if self.style_type in types:
                return att

        return False

    def fromdefault(self):
        self.name = StyleAbstract.default_name[self.style_type]

        if self.style_type in ["paragraph", "character"]:
            self.font = StyleAbstract.default_font

        # TODO Le reste

        return True

    def fromxml(self, xml, onlybool=False):

        if xml.tag == StyleAbstract.type_xml[self.style_type]:

            #--- Name ----------------------------------------------

            if self.style_type in ["paragraph", "table", "cell", "character"]:
                name_att = self._choose_att(StyleAbstract.name_xml)

            if (name := xml.get(name_att)) is not None:
                self.name = name

            #--- Common attributes ---------------------------------

            if (default := xml.get("DefaultStyle")) is not None:
                self.is_default = xmlc.num_to_bool(default)

            #--- Specific attributes for paragraph -----------------
            # Moved in ParagraphStyle

            #--- Specific attributes for character -----------------
            # Moved in CharacterStyle

            #--- Specific attributes for table ---------------------

            if self.style_type == "table":
                pass

            #--- Specific attributes for cell ----------------------

            if self.style_type == "cell":

                for case in ["left", "right", "top", "bottom"]:
                    att = xml.get("{}Padding".format(case.capitalize()))

                    if att is not None:
                        self.padding[case] = att

            #--- Common attributes to paragraphs + characters ------

            if self.style_type in ["paragraph", "character"]:
                #--- Font and font features ------------------------------

                if (font := xml.get("FONT")) is not None:
                    self.font["name"] = font

                if (font_size := xml.get("FONTSIZE")) is not None:
                    self.font["size"] = float(font_size)

                if (font_features := xml.get("FONTFEATURES")) is not None:
                    self.font["features"] = font_features.split(",")

                if (font_color := xml.get("FCOLOR")) is not None:
                    self.font["color"] = font_color

                # NOTE Weird FEATURES duplicate
                if (features := xml.get("FEATURES")) is not None:
                    self.features = features

                #--- Lang ------------------------------------------------

                if (lang := xml.get("LANGUAGE")) is not None:
                    if lang:
                        self.lang = lang

                #--- Parent style ----------------------------------------

                parent_att = self._choose_att(StyleAbstract.parent_xml)

                if (parent := xml.get(parent_att)) is not None:
                    if parent:
                        self.parent = parent

                #--- Shortcut --------------------------------------------

                shortcut_att = self._choose_att(StyleAbstract.shortcut_xml)

                if (shortcut := xml.get(shortcut_att)) is not None:
                    if shortcut:
                        self.shortcut = shortcut

            #--- Common attributes to tables, celles, characters ---

            if self.style_type in ["table", "cell", "character", "paragraph"]:
                fshade_att = self._choose_att(StyleAbstract.fshade_xml)
                fcolor_att = self._choose_att(StyleAbstract.fcolor_xml)

                if (fill_color := xml.get(fcolor_att)) is not None:
                    self.fill["color"] = fill_color

                if (fill_shade := xml.get(fshade_att)) is not None:
                    self.fill["shade"] = float(fill_shade)

            #--- Childs --------------------------------------------

            # Moved StyleTabs check in ParagraphStyle

            #-------------------------------------------------------

            #--- FIXME This records undocumented attributes --------

            self.undocumented = xmlc.all_undocumented_to_python(xml)

            # ------------------------------------------------------

            # Returns lxml.etree._Element instead of True, for
            # inheritance purposes

            if onlybool:
                return True
            else:
                return xml
        else:
            return False

    def toxml(self):
        xml = ET.Element(StyleAbstract.type_xml[self.style_type])

        #--- Name ----------------------------------------------

        if self.style_type in ["paragraph", "table", "cell", "character"]:
            name_att = self._choose_att(StyleAbstract.name_xml)

        xml.attrib[name_att] = self.name

        #--- Common attributes ---------------------------------

        if self.is_default:
            xml.attrib["DefaultStyle"] = xmlc.bool_to_num(self.is_default)

        #--- Specific attributes for table ---------------------

        if self.style_type == "table":
            pass

        #--- Specific attributes for cell ----------------------

        if self.style_type == "cell":

            for case in ["left", "right", "top", "bottom"]:
                att_name = "{}Padding".format(case.capitalize())
                xml.attrib[att_name] = self.padding[case]

        #--- Common attributes to paragraphs + characters ------

        if self.style_type in ["paragraph", "character"]:

            if self.font["name"]:
                xml.attrib["FONT"] = self.font["name"]

            if self.style_type == "character":
                xml.attrib["FONTSIZE"] = str(self.font["size"])

            # TODO FIXME Handle font features as a dict instead
            # of a list, like in other styles
            # xml.attrib["FONTFEATURES"] = " ".join(self.font["features"].keys())

            if self.font["features"]:
                xml.attrib["FONTFEATURES"] = ",".join(self.font["features"])

            if self.font["color"]:
                xml.attrib["FCOLOR"] = self.font["color"]

            if self.features:
                xml.attrib["FEATURES"] = self.features

            if self.lang is not None:
                xml.attrib["LANGUAGE"] = self.lang

            if self.shortcut is not None:
                shortcut_att = self._choose_att(StyleAbstract.shortcut_xml)
                xml.attrib[shortcut_att] = self.shortcut

            if self.parent is not None:
                # Parent style of same style type
                # CPARENT -> parent character style for this character style
                # PARENT  -> parent paragraph style for this paragraph style
                parent_att = self._choose_att(StyleAbstract.parent_xml)
                xml.attrib[parent_att] = self.parent

        #--- Common attributes to tables, celles, characters ---

        if self.style_type in ["table", "cell", "character"]:
            fshade_att = self._choose_att(StyleAbstract.fshade_xml)
            fcolor_att = self._choose_att(StyleAbstract.fcolor_xml)

            xml.attrib[fcolor_att] = xmlc.none_or_str(self.fill["color"])

            if self.fill["shade"] is not None:
                xml.attrib[fshade_att] = xmlc.float_or_int_string(
                    self.fill["shade"]
                )

        #-------------------------------------------------------

        #--- FIXME This exports undocumented attributes -------

        try:
            if self.style_type != "paragraph":
                xml, undoc_attribs = xmlc.all_undocumented_to_xml(
                    xml, self.undocumented, True,
                    self.style_type + " style"
                )

        except AttributeError:
            # NOTE If fromxml was not used
            pass

        return xml

    def fromstyle(self, style, override=False):
        """
        Set attributes according to another style.

        :type style: ParagraphStyle, CharacterStyle, ...
        :param style: Style to load attributes from.
        :type override: boolean
        :param override: Override attributes that differs from style
        """
        # TODO
        pass


class ParagraphStyle(StyleAbstract):
    """
    Paragraph style in SLA (STYLE)

    :type default: boolean
    :param default: Use default settings (False by default)
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    +--------------+------------------------------------+
    | Kwargs       | Setting                            |
    +==============+====================================+
    | name         | Style name                         |
    +--------------+------------------------------------+
    | defaultstyle | Scribus default paragraph style?   |
    +--------------+------------------------------------+
    | parent       | Parent style name (paragraph)      |
    +--------------+------------------------------------+
    | cparent      | Parent style name (character)      |
    +--------------+------------------------------------+
    | alignment    | Text alignment. Must be in         |
    |              | ``pyscribus.common.xml.alignment`` |
    |              | keys                               |
    +--------------+------------------------------------+
    | font         | Font name                          |
    +--------------+------------------------------------+
    | fontsize     | Font size                          |
    +--------------+------------------------------------+
    | spacebefore  | Space before paragraph             |
    +--------------+------------------------------------+
    | spaceafter   | Space after paragraph              |
    +--------------+------------------------------------+
    | leading      | Leading mode. Must be in           |
    |              | ``ParagraphStyle.leading_xml``.    |
    |              | If "fixed" mode, you must define   |
    |              | leadingValue setting.              |
    +--------------+------------------------------------+
    | leadingValue | Leading value in pica points if    |
    |              | leading mode is "fixed".           |
    +--------------+------------------------------------+
    | default      | Equivalent to a fromdefault        |
    |              | call, value being True or the      |
    |              | default name                       |
    +--------------+------------------------------------+

    :Example:

    .. code:: python

       title_style = styles.ParagraphStyle(
           name="Title", fontsize=18, alignment="center",
           leading="fixed", leadingValue=16
       )

       normal_style = styles.ParagraphStyle(
           name="Normal", fontsize=12, alignment="justify",
           leading="automatic"
       )

    """

    leading_xml = {
        "fixed": "0",
        "automatic": "1",
        "grid": "2",
    }

    def __init__(self, doc_parent, default=False, **kwargs):
        StyleAbstract.__init__(self, "paragraph", doc_parent, default)
        self._quick_setup(kwargs)

    def fromxml(self, xml):
        is_paragraph = StyleAbstract.fromxml(self, xml, True)

        if is_paragraph:

            #--- Lists ------------------------------------------------------

            self.is_ul,self.is_ol = False,False

            if (is_bullet := xml.get("Bullet")) is not None:
                if is_bullet == "1":
                    self.is_ul = True

            if (is_numeroted := xml.get("Numeration")) is not None:
                if is_numeroted == "1":
                    self.is_ol = True

            if self.is_ol and self.is_ul:
                raise exceptions.InsaneSLAValue(
                    "Style {} is both bullet and numeroted list.".format(name)
                )

            if self.is_ul:
                if (bullet_char := xml.get("BulletStr")) is not None:
                    # TODO
                    pass

            #--- Parent character style -------------------------------------

            if (character_parent := xml.get("CPARENT")) is not None:
                self.character_parent = character_parent

            #--- Leading ----------------------------------------------------

            if (leading := xml.get("LINESPMode")) is not None:

                for human, code in ParagraphStyle.leading_xml.items():
                    if leading == code:
                        self.leading["mode"] = human
                        break

                if self.leading["mode"] == "fixed":
                    leading_value = xml.get("LINESP")

                    if leading_value is not None:
                        self.leading["value"].value = float(leading_value)

            #--- Alignment --------------------------------------------------

            if (alignment := xml.get("ALIGN")) is not None:
                for human, code in xmlc.alignment.items():
                    if alignment == code:
                        self.font["alignment"] = human
                        break

            #--- Spaces before and after paragraph --------------------------

            for case in [["VOR", "before"], ["NACH", "after"]]:

                if (space_att := xml.get(case[0])) is not None:
                    self.space[case[1]] = dimensions.Dim(float(space_att))

            #--- Tabs -------------------------------------------------------

            for child in xml:

                if child.tag == "Tabs":
                    to = StyleTab()

                    if (success := to.fromxml(child)):
                        self.tabs.append(to)

            #--- End of parsing ---------------------------------------------

            return True
        else:
            return False

    def toxml(self):
        xml = StyleAbstract.toxml(self)

        #------------------------------------------------------------

        xml.attrib["ALIGN"] = xmlc.alignment[self.font["alignment"]]

        if self.leading["mode"] is not None:
            xml.attrib["LINESPMode"] = ParagraphStyle.leading_xml[self.leading["mode"]]

            if self.leading["mode"] == "fixed":
                xml.attrib["LINESP"] = self.leading["value"].toxmlstr()

        #--- Parent character style ---------------------------------

        # NOTE To not confuse with parent paragraph style which is
        # in @PARENT, and handled in StyleAbstract

        if self.character_parent:
            xml.attrib["CPARENT"] = self.character_parent

        for case in [["before", "VOR"], ["after", "NACH"]]:
            if self.space[case[0]] is not None:
                xml.attrib[case[1]] = self.space[case[0]].toxmlstr(True)

        # xml.attrib["VOR"] = self.space["before"].toxmlstr()
        # xml.attrib["NACH"] = self.space["after"].toxmlstr()

        #--- FONT SIZE ----------------------------------------------

        font_size = str(self.font["size"])

        if self.character_parent and font_size == "0":
            # If the font size of the paragraph is not defined
            # because it is defined in a parent character style,
            # don't write FONTSIZE attribute
            pass
        else:
            if font_size != "0":
                xml.attrib["FONTSIZE"] = font_size
            # else:
                # raise exceptions.InsaneSLAValue(
                    # "Paragraph style '{}' has no parent character style and a"
                    # "fontsize equal to zero.".format(
                        # self.name
                    # )
                # )

        #------------------------------------------------------------

        try:
            xml, undoc_attribs = xmlc.all_undocumented_to_xml(
                xml, self.undocumented, True,
                self.style_type + " style"
            )

        except AttributeError:
            # NOTE If fromxml was not used
            pass

        return xml

    def fromdefault(self):
        StyleAbstract.fromdefault(self)

        self.leading = {
            "mode": None,
            "value": dimensions.Dim(12)
        }

        return True

    def _quick_setup(self, settings):
        """
        Method for defining style settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            StyleAbstract._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                if setting_name == "spacebefore":
                    self.space["before"] = dimensions.Dim(float(setting_value))

                if setting_name == "spaceafter":
                    self.space["after"] = dimensions.Dim(float(setting_value))

                if setting_name == "cparent":
                    self.character_parent = setting_value

                if setting_name == "leading":
                    if setting_value in ParagraphStyle.leading_xml:
                        self.leading["mode"] = setting_value

                if setting_name == "leadingValue":
                    self.leading["value"] = dimensions.Dim(float(setting_value))

                if setting_name == "alignment":

                    if setting_value.lower() in xmlc.alignment.keys():
                        self.font["alignment"] = setting_value
                    else:
                        raise ValueError(
                            "Wrong alignement setting '{}'. "
                            "Alignement setting must be {}".format(
                                setting_value,
                                ", ".join(xmlc.alignment.keys())
                            )
                        )

    def set_leadingmode(self, leadingmode):
        """
        Set leading mode.

        :type leadingmode: string
        :param leadingmode: "fixed", "automatic", "grid"
        """

        if leadingmode.lower() in ParagraphStyle.leading_xml:
            self.leading["mode"] = leadingmode
            return True
        else:
            raise ValueError()


class CharacterStyle(StyleAbstract):
    """
    Character style in SLA (CHARSTYLE)

    :type default: boolean
    :param default: Use default settings (False by default)
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    +--------------+-----------------------------+----------+
    | Kwargs       | Setting                     | Type     |
    +==============+=============================+==========+
    | name         | Style name                  | string   |
    +--------------+-----------------------------+----------+
    | defaultstyle | Scribus default character   | boolean  |
    |              | style ?                     | boolean  |
    +--------------+-----------------------------+----------+
    | parent       | Parent style name           | string   |
    +--------------+-----------------------------+----------+
    | font         | Font name                   | string   |
    +--------------+-----------------------------+----------+
    | fontsize     | Font size                   | string   |
    +--------------+-----------------------------+----------+
    | default      | Equivalent to a fromdefault | boolean, |
    |              | call, value being True or   | string   |
    |              | the default name.           |          |
    +--------------+-----------------------------+----------+
    """

    def __init__(self, doc_parent, default=False, **kwargs):
        StyleAbstract.__init__(self, "character", doc_parent, default)
        StyleAbstract._quick_setup(self, kwargs)

    def fromxml(self, xml):
        is_character = StyleAbstract.fromxml(self, xml, True)

        if is_character:

            #--- Scales -----------------------------------------------------

            for case in [["SCALEH", "horizontal"], ["SCALEV", "vertical"]]:

                if (scale_att := xml.get(case[0])) is not None:
                    self.scale[case[1]] = scale_att

            #--- End of parsing ---------------------------------------------

            return True
        else:
            return False

    def toxml(self):
        xml = StyleAbstract.toxml(self)

        #--- Scales -----------------------------------------------------

        xml.attrib["SCALEH"] = str(self.scale["horizontal"])
        xml.attrib["SCALEV"] = str(self.scale["vertical"])

        return xml


class TabularStyleAbstract(StyleAbstract):
    """Abstract middle class for Table and Cell styles."""

    def __init__(self, style_type, doc_parent, default=False, **kwargs):
        StyleAbstract.__init__(self, style_type, doc_parent, default)

    def fromxml(self, xml):
        x = StyleAbstract.fromxml(self, xml)

        if len(x):

                for border in x:

                    if border.tag in TableBorder.sides_xml.values():
                        tb = TableBorder()

                        if (success := tb.fromxml(border)):
                            self.borders.append(tb)

                return True

        return False

    def toxml(self):
        xml = StyleAbstract.toxml(self)

        for border in self.borders:
            bx = border.toxml()
            xml.append(bx)

        return xml


class TableBorder(xmlc.PyScribusElement):
    """
    Table border settings in SLA 
    (TableBorderLeft, TableBorderRight, TableBorderTop, TableBorderBottom)

    :type side: str
    :param side: (Cell) Side of the border
    """

    sides_xml = {
            "left": "TableBorderLeft",
            "right": "TableBorderRight",
            "top": "TableBorderTop",
            "bottom": "TableBorderBottom"
    }

    def __init__(self, side=False):
        super().__init__()

        if side:
            if side.lower() in TableBorder.sides_xml.keys():
                self.side = side.lower()
            else:
                self.side = False
        else:
            self.side = False

        self.lines = []

        self.width = None

    def fromxml(self, xml):
        self.side = False

        # Find the side of the table border -------------------------

        if xml.tag in TableBorder.sides_xml.values():

            for h,x in TableBorder.sides_xml.items():
                if x == xml.tag:
                    self.side = h
                    break

        if not self.side:
            msg = "Invalid side for TableBorder"

            if self.style_type == "table":
                msg += " in TableStyle"

            if self.style_type == "cell":
                msg += " in CellStyle"

            raise exceptions.InsaneSLAValue(msg)

        # If the table border's side was found ----------------------

        # -------------------------------------------------

        if (width := xml.get("Width")) is not None:
            self.width = dimensions.Dim(float(width))

        # -------------------------------------------------

        for line in xml:

            if line.tag == "TableBorderLine":
                lo = TableBorderLine()

                if (success := lo.fromxml(line)):
                    self.lines.append(lo)

        return True

    def toxml(self):
        xml = ET.Element(TableBorder.sides_xml[self.side])

        if self.width is not None:
            xml.attrib["Width"] = self.width.toxmlstr(True)

        for line in self.lines:
            lx = line.toxml()
            xml.append(lx)

        return xml


class TableBorderLine(xmlc.PyScribusElement):
    """
    Cell border line in SLA (TableBorderLine)
    """

    def __init__(self):
        super().__init__()

        self.width = 0
        self.pen_style = "1"
        self.color = "Black"
        self.shade = 100

    def fromdefault(self):
        self.width = 1
        self.pen_style = "1"
        self.color = "Black"
        self.shade = 100

    def fromxml(self, xml):
        if xml.tag == "TableBorderLine":

            if (width := xml.get("Width")) is not None:
                self.width = float(width)

            if (color := xml.get("Color")) is not None:
                self.color = color

            if (shade := xml.get("Shade")) is not None:
                self.shade = int(shade)

            if (style := xml.get("PenStyle")) is not None:
                self.pen_style = style

            return True

        else:
            return False

    def toxml(self):
        xml = ET.Element("TableBorderLine")

        if float(self.width) == int(self.width):
            xml_width = int(self.width)
        else:
            xml_width = self.width

        xml.attrib["Width"] = str(xml_width)
        xml.attrib["PenStyle"] = str(self.pen_style)
        xml.attrib["Color"] = self.color
        xml.attrib["Shade"] = str(self.shade)

        return xml


class TableStyle(TabularStyleAbstract):
    """
    Table style in  (TableStyle)
    """

    def __init__(self, doc_parent, default=False, **kwargs):
        TabularStyleAbstract.__init__(self, "table", doc_parent, default)


class CellStyle(TabularStyleAbstract):
    """
    Cell style in SLA (CellStyle)
    """

    def __init__(self, doc_parent, default=False, **kwargs):
        TabularStyleAbstract.__init__(self, "cell", doc_parent, default)


class StyleTab(xmlc.PyScribusElement):
    tab_type_xml = {
        "left": "0", "right": "1",
        "period": "2", "comma": "3",
        "center": "4",
    }

    def __init__(self):
        super().__init__()

        self.type = False
        self.fill = False
        self.position = dimensions.Dim(0, "pica")

    def fromxml(self, xml):
        """
        """

        if (tab_type := xml.get("Type")) is not None:
            try:
                for human,code in StyleTab.tab_type_xml.items():
                    if code == tab_type:
                        self.type = human
                        break

            except IndexError:
                self.type = "left"

        if (pos := xml.get("Pos")) is not None:
            pos = float(pos)
            self.position.value = pos

        if (fill := xml.get("Fill")) is not None:
            self.fill = fill

        return True

    def toxml(self):
        xml = ET.Element()
        xml.attrib["Type"] = StyleTab.tab_type_xml(self.type)
        xml.attrib["Pos"] = self.position.toxmlstr()
        xml.attrib["Fill"] = self.fill

        return xml

    def fromdefault(self):
        self.type = "left"
        self.fill = False
        self.position = dimensions.Dim(0, "pica")

        return True


class RuleStyle(xmlc.PyScribusElement):
    """
    Rule style (filet) in SLA (MultiLine)
    """

    def __init__(self):
        super().__init__()

        self.name = None
        self.lines = []

    def fromxml(self, xml):
        """
        """

        if xml.tag == "MultiLine":

            if (name := xml.get("Name")) is not None:
                self.name = name

            for element in xml:

                if element.tag == "SubLine":
                    sl = RuleStyleLine()

                    if (success := sl.fromxml(element)):
                        self.lines.append(sl)

            return True

        return False

    def toxml(self):
        """
        """

        xml = ET.Element("MultiLine")
        xml.attrib["Name"] = self.name

        for line in self.lines:
            lx = line.toxml()
            xml.append(lx)

        return xml


class RuleStyleLine(xmlc.PyScribusElement):
    """
    Sub-line in rule style in SLA (MultiLine/SubLine)
    """

    # Line end human <-> XML
    lineend_xml = {"square": "16", "round": "32", "flat": "0"}

    # Line join human <-> XML
    linejoin_xml = {"pointy": "0", "bevelled": "64", "round": "128"}

    # Line style human <-> XML
    dash_xml = {
        # Most common and named line styles

        "line": "1",
        "dashed": "2",
        "dots": "3",
        "line-dash": "4",
        "line-dash-dash": "5",

        # Here be dragons, and a lot of untitled line styles

        "untitled-6": "6", "untitled-7": "7", "untitled-8": "8",
        "untitled-9": "9", "untitled-10": "10", "untitled-11": "11",
        "untitled-12": "12", "untitled-13": "13", "untitled-14": "14",
        "untitled-15": "15", "untitled-16": "16", "untitled-17": "17",
        "untitled-18": "18", "untitled-19": "19", "untitled-20": "20",
        "untitled-21": "21", "untitled-22": "22", "untitled-23": "23",
        "untitled-24": "24", "untitled-25": "25", "untitled-26": "26",
        "untitled-27": "27", "untitled-28": "28", "untitled-29": "29",
        "untitled-30": "30", "untitled-31": "31", "untitled-32": "32",
        "untitled-33": "33", "untitled-34": "34", "untitled-35": "35",
        "untitled-36": "36", "untitled-37": "37",
    }

    def __init__(self):
        super().__init__()

        self.color = None
        self.shortcut = ""

        self.width = None
        self.opacity = None

        self.end = None
        self.join = None
        self.style = None

    def fromdefault(self):
        self.end = "flat"
        self.join = "pointy"
        self.opacity = dimensions.Dim(100, "pc")

    def fromxml(self, xml):
        """
        """

        if xml.tag == "SubLine":
            # --- Shortcut -----------------------------------------------

            if (shortcut := xml.get("Shortcut")) is not None:
                self.shortcut = shortcut

            # --- Color and opacity --------------------------------------

            if (color := xml.get("Color")) is not None:
                self.color = color

            if (opacity := xml.get("Shade")) is not None:
                self.opacity = dimensions.Dim(float(opacity), "pc")

            # --- Line width ---------------------------------------------

            if (width := xml.get("Width")) is not None:
                self.width = dimensions.Dim(float(width))

            # --- Line style ---------------------------------------------

            if (dash := xml.get("Dash")) is not None:

                for human, code in RuleStyleLine.dash_xml.items():
                    if code == dash:
                        self.style = human
                        break

            # --- Line end -----------------------------------------------

            if (line_end := xml.get("LineEnd")) is not None:

                for human, code in RuleStyleLine.lineend_xml.items():
                    if code == line_end:
                        self.end = human
                        break

            # --- Line join ----------------------------------------------

            if (line_join := xml.get("LineJoin")) is not None:

                for human, code in RuleStyleLine.linejoin_xml.items():
                    if code == line_join:
                        self.join = human
                        break

            return True

        return False

    def toxml(self):
        """
        """

        xml = ET.Element("SubLine")

        # --- Color and opacity --------------------------------------

        if self.color is not None:
            xml.attrib["Color"] = self.color

        if self.opacity is not None:
            xml.attrib["Shade"] = self.opacity.toxmlstr(True)
        else:
            xml.attrib["Shade"] = "100"

        # --- Line style, end, join ----------------------------------

        xml.attrib["Dash"] = RuleStyleLine.dash_xml[self.style]
        xml.attrib["LineEnd"] = RuleStyleLine.lineend_xml[self.end]
        xml.attrib["LineJoin"] = RuleStyleLine.linejoin_xml[self.join]

        # --- Line width ---------------------------------------------

        if self.width is not None:
            xml.attrib["Width"] = self.width.toxmlstr(True)

        # --- Shortcut -----------------------------------------------

        xml.attrib["Shortcut"] = self.shortcut

        return xml

# Fonctions =============================================================#

def fromSLA(filepath="", slastring=""):
    """
    Parse a SLA file / string and returns a dictionary of all styles in it.

    :type filepath: string
    :param filepath: SLA filepath
    :type slastring: string
    :param slastring: SLA XML string
    :rtype: dict,boolean
    :returns: Dictionary of styles usable by document.Document, or False
    """

    styles = {
        "note": [],
        "paragraph": [],
        "character": [],
        "table": [],
        "rule": []
    }

    if filepath:
        xml = ET.parse(filepath).getroot()
    else:
        xml = ET.fromstring(slastring)

    if len(xml):

        for style_type in [
                [TableStyle, "table", "DOCUMENT/TableStyle"],
                [ParagraphStyle, "paragraph", "DOCUMENT/STYLE"],
                [CharacterStyle, "character", "DOCUMENT/CHARSTYLE"],
                [NoteStyle, "note", "DOCUMENT/NotesStyles/notesStyle"],
                [RuleStyle, "rule", "DOCUMENT/MultiLine"]
            ]:

            tmp_styles = xml.findall(style_type[2])

            if len(tmp_styles):

                for style_item in tmp_styles:
                    si = style_type[0]()
                    success = si.fromxml(style_item)

                    if success:
                        styles[style_type[1]].append(si)

        return styles
    else:
        return False

# vim:set shiftwidth=4 softtabstop=4 spl=en:
