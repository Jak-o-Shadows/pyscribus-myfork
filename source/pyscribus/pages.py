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
Classes for SLA Pages / Master pages.
"""

# Scribus pages are  arranged in a vast scratch space,  where 1 unit ==
# 1/72 inch.  Positive x is to  the right, and positive  y is downward.
# The positions, width and height in  the elements are in scratch space
# coordinates  with the  exception  of POCOOR  and COCOOR  coordinates,
# which are in the rotated and translated space of a PAGEOBJECT.

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions
import pyscribus.dimensions as dimensions

from pyscribus.common.xml import *

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class PageAbstract(PyScribusElement):
    """
    Abstract class for pages and master pages.

    Use Page or MasterPage classes instead.

    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table in Page, MasterPage)

    .. seealso:: :class:`MasterPage`, :class:`Page`
    """

    orientation_xml = {"portrait": "0", "landscape": "1"}

    autoguides_origin_xml = {"page": "0", "margins": "1"}

    def __init__(self, **kwargs):
        PyScribusElement.__init__(self)

        self.box = dimensions.DimBox()

        self.borders = {
            "top": dimensions.Dim(40),
            "left": dimensions.Dim(40),
            "right": dimensions.Dim(40),
            "bottom": dimensions.Dim(40),
        }

        self.name = ""
        self.master_name = ""

        self.orientation = "portrait"

        self.paper_size = ""

        self.number = -1

        #--- FIXME Tester pour savoir comment constituer les listes ------

        self.guides = {
            "horizontal": [],
            "vertical": []
        }

        #--- FIXME Not documented ----------------------------------------

        # For multipage spreads, which page in the spread is the left most
        # LEFT="0"

        # PRESET="0"

        #--- Auto guides -------------------------------------------------

        # FIXME Understand AGSelection usage
        # AGSelection="0 0 0 0"

        self.auto_guides = {
            "lines": {
                "count": 0,
                "gap": dimensions.Dim(0),
                "origin": "page"
            },
            "columns": {
                "count": 0,
                "gap": dimensions.Dim(0),
                "origin": "page"
            },
            "selection": []
        }

        #--- FIXME Not documented ----------------------------------------

        # Same as DOCUMENT/PDF/Effekte (PDF display effects) attributes ?
        # pageEffectDuration="1"
        # pageViewDuration="1"
        # effectType="0"
        # Dm="0"
        # M="0"
        # Di="0"/>

        #-----------------------------------------------------------------

        if kwargs:
            self._quick_setup(kwargs)

    def _quick_setup(self, settings):
        """
        Method for defining (master)page settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            PyScribusElement._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                # (Master) page box -------------------------------------------

                if setting_name == "posx":
                    # self.box.coords["top-left"][0].value = float(setting_value)
                    self.box.setx("top-left", float(setting_value))

                if setting_name == "posy":
                    # self.box.coords["top-left"][1].value = float(setting_value)
                    self.box.sety("top-left", float(setting_value))

                if setting_name == "width":
                    self.box.dims["width"].value = float(setting_value)

                if setting_name == "height":
                    self.box.dims["height"].value = float(setting_value)

                # Borders -----------------------------------------------------

                if setting_name in [
                        "rightborder", "leftborder",
                        "topborder", "bottomborder"]:
                    side = setting_name.split("border")[0]
                    self.borders[side].value = float(setting_value)

                if setting_name == "borders":
                    # NOTE We solve borders settings like CSS margin property
                    # If only one value : same border for all sides
                    # If two values: vertical and horizontal borders
                    # If three values: top horizontal bottom
                    # If four values: top right bottom left

                    if isinstance(setting_value, list):
                        setting_len = len(setting_value)

                        if setting_len == 1:

                            for side in ["top", "right", "bottom", "left"]:
                                self.borders[side].value = float(
                                    setting_value[0]
                                )

                        if setting_len == 2:
                            sides = zip(
                                [["top", "bottom"], ["right", "left"]],
                                setting_value
                            )

                            for side in sides:
                                for s in side[0]:
                                    self.borders[s].value = float(side[1])

                        if setting_len == 3:
                            self.borders["top"].value = float(setting_value[0])

                            for side in ["right", "left"]:
                                self.borders[side].value = float(
                                    setting_value[1]
                                )

                            self.borders["bottom"].value = float(
                                setting_value[2]
                            )

                        if setting_len == 4:
                            sides = zip(
                                ["top", "right", "bottom", "left"],
                                setting_value
                            )

                            for side in sides:
                                self.borders[side[0]].value = float(side[1])

                # -------------------------------------------------------------

    def set_orientation(self, orientation):
        """
        Set (master) page orientation.

        :param orientation: "portrait" or "landscape"
        :type orientation: string
        :returns: boolean
        :rtype: boolean
        """

        if orientation.lower() in PageAbstract.orientation_xml.keys():
            self.orientation = orientation.lower()
            # FIXME TODO Modify (master) page box accordingly

            return True

        else:
            raise ValueError(
                "orientation parameter of set_orientation must be "\
                "portrait' or 'landscape'"
            )

    def fromxml(self, xml, master=False):
        """
        Set (master) page attributes according to LXML Element

        :param xml: (Master) page source as XML element
        :type xml: lxml._Element
        :param master: If the page is a master page or not
        :type master: boolean
        :returns: boolean
        :rtype: boolean
        """
        if master:
            tag = "MASTERPAGE"
        else:
            tag = "PAGE"

        if xml.tag == tag:
            #--- Box settings -------------------------------------

            posx = xml.get("PAGEXPOS")
            posy = xml.get("PAGEYPOS")
            dim_width = xml.get("PAGEWIDTH")
            dim_height = xml.get("PAGEHEIGHT")

            valid_box = 0

            for test in [posx, posy, dim_width, dim_height]:
                if test is not None:
                    valid_box += 1

            if valid_box == 4:

                self.box.set_box(
                    top_lx=posx, top_ly=posy,
                    width=dim_width, height=dim_height
                )

            #--- Name / Master page name --------------------------

            self.name = xml.get("NAM")
            self.master_name = xml.get("MNAM")

            #--- Page number --------------------------------------

            page_number = xml.get("NUM")

            if page_number is not None:
                # NOTE Page 0 is the first page so we adjust to a human
                # readable count
                self.number = int(page_number) + 1

            #--- Paper size name and orientation ------------------

            if (paper_size := xml.get("Size")) is not None:
                self.paper_size = paper_size

            if (orientation := xml.get("Orientation")) is not None:

                for h,x in PageAbstract.orientation_xml.items():
                    if orientation == x:
                        self.orientation = h
                        break

            #--- Borders ------------------------------------------

            for b in ["left", "top", "bottom", "right"]:
                att = "BORDER{}".format(b.upper())
                self.borders[b] = dimensions.Dim(float(xml.get(att)))

            #--- Guides -------------------------------------------

            for guide_type in ["vertical", "horizontal"]:

                att_name = "{}Guides".format(guide_type.capitalize())

                if (att := xml.get(att_name)) is not None:
                    if att:
                        # NOTE Example of att value : "42.5197 56.6929 "

                        guides_list = []
                        guides_values = [g.strip() for g in att.split(" ")]

                        for g in guides_values:

                            if g:

                                guides_list.append(
                                    dimensions.Dim(float(g))
                                )

                        # self.guides[guide_type] = att
                        self.guides[guide_type] = guides_list

            #--- Auto guides --------------------------------------

            for case in [["lines", "horizontal"], ["columns", "vertical"]]:
                ag_count = xml.get("AG{}AutoCount".format(case[1]))
                ag_gap = xml.get("AG{}AutoGap".format(case[1]))
                ag_origin = xml.get("AG{}AutoRefer".format(case[1]))

                if ag_count is not None:
                    ag_count = int(ag_count)
                    self.auto_guides[case[0]]["count"] = ag_count

                if ag_gap is not None:
                    ag_gap = float(ag_gap)
                    self.auto_guides[case[0]]["gap"].value = ag_count

                if ag_origin is not None:

                    for human,code in PageAbstract.autoguides_origin_xml.items():
                        if ag_origin == code:
                            self.auto_guides[case[0]]["origin"] = human

            #--- FIXME This records undocumented attributes -------

            self.undocumented = all_undocumented_to_python(xml)

            # self.undocumented = undocumented_to_python(
                # xml,
                # [
                    # "LEFT", "PRESET",
                    # "AGSelection",
                    # "pageEffectDuration", "pageViewDuration", "effectType",
                    # "Dm", "M", "Di"
                # ]
            # )

            return True

        return False

    def toxml(self, master=False):
        """
        Returns (master) page as LXML Element

        :param master: If the page is a master page or not
        :type master: bool
        :returns: xml
        :rtype: lxml._Element
        """

        #--- Appropriate tag if master page or page -----------

        if master:
            tag = "MASTERPAGE"
        else:
            tag = "PAGE"

        xml = ET.Element(tag)

        #--- Size and dimensions ------------------------------

        xml.attrib["PAGEXPOS"] = self.box.coords["top-left"][0].toxmlstr()
        xml.attrib["PAGEYPOS"] = self.box.coords["top-left"][1].toxmlstr()

        xml.attrib["PAGEWIDTH"] = self.box.dims["width"].toxmlstr()
        xml.attrib["PAGEHEIGHT"] = self.box.dims["height"].toxmlstr()

        #--- Borders ------------------------------------------

        for b in ["left", "right", "top", "bottom"]:
            att = "BORDER{}".format(b.upper())
            xml.attrib[att] = self.borders[b].toxmlstr(True)

         #--- Page number --------------------------------------

        if self.number > 0:
            # NOTE Page 0 is the first page so we adjust back
            # from human counting to computer counting
            xml.attrib["NUM"] = str(self.number - 1)

        #--- Page name and master page name -------------------

        xml.attrib["NAM"] = self.name
        xml.attrib["MNAM"] = self.master_name

        #--- (Master) page size name and orientation ----------

        xml.attrib["Size"] = self.paper_size
        xml.attrib["Orientation"] = PageAbstract.orientation_xml[self.orientation]

        #--- Guides -------------------------------------------


        for guide_type,guides in self.guides.items():
            att_name = "{}Guides".format(guide_type.capitalize())

            # NOTE Example of att value : "42.5197 56.6929 "

            guides_str = " ".join([g.toxmlstr() for g in guides])

            if guides_str.strip():
                xml.attrib[att_name] = guides_str

        #--- Auto guides --------------------------------------

        # Page lines count
        # AGhorizontalAutoCount="2"
        # Page lines gap (gouttière)
        # AGhorizontalAutoGap="17.007874015748"
        # Page lines origin
        # 0 = Page 1 = Margins
        # AGhorizontalAutoRefer="0"

        # Page columns count
        # AGverticalAutoCount="3"
        # Page columns gap (gouttière)
        # AGverticalAutoGap="22.6771653543307"
        # Page column origin
        # 0 = Page 1 = Margins
        # AGverticalAutoRefer="0"

        #--- FIXME This exports undocumented attributes -------

        try:
            # xml = undocumented_to_xml(xml, self.undocumented)
            xml, undoc_attribs = all_undocumented_to_xml(
                xml, self.undocumented, True, tag
            )

        except AttributeError:
            # NOTE If fromxml was not used
            pass

        return xml

    def fromdefault(self, master=False, default=False):
        """
        Set (master) page attributes according to known defaults.

        :param master: If the page is a master page or not
        :param default: Name of the set of defaults ("a4", "letter")
        :type master: bool
        :type default: str
        """

        for border in self.borders.values():
            border.value = 40

        dim_default = "a4"

        if default:
            for format_name in ["a4", "letter"]:
                if default.lower() == format_name:
                    dim_default = format_name
                    break

        self.master_name = "Normal"

        self.box.dims["width"].fromdefault("{}-width".format(dim_default))
        self.box.dims["height"].fromdefault("{}-height".format(dim_default))

        self.box.set_box(
            top_lx=100.0, top_ly=20.0,
            width=self.box.dims["width"].value,
            height=self.box.dims["height"].value
        )


class Page(PageAbstract):
    """
    Page in SLA

    To add objects to this page, use Document.append()

    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    +--------------+--------------------------------+------------+
    | Kwargs       | Setting                        | Value type |
    +==============+================================+============+
    | default      | Equivalent to a fromdefault    | boolean or |
    |              | call, value being the default  | string     |
    |              | name or True                   |            |
    +--------------+--------------------------------+------------+
    | posx         | X position of the page         | float      |
    +--------------+--------------------------------+------------+
    | posy         | Y position of the page         | float      |
    +--------------+--------------------------------+------------+
    | width        | Page width                     | float      |
    +--------------+--------------------------------+------------+
    | height       | Page height                    | float      |
    +--------------+--------------------------------+------------+
    | borders      | Shorthand for rightborder,     | List of    |
    |              | leftborder, topborder,         | floats     |
    |              | bottomborder.                  |            |
    |              |                                |            |
    |              | Read like the CSS margin       |            |
    |              | property:                      |            |
    |              |                                |            |
    |              | **With 1 float in the list :** |            |
    |              |                                |            |
    |              | [top & right & bottom & left]  |            |
    |              |                                |            |
    |              | **With 2 float in the list :** |            |
    |              |                                |            |
    |              | [top & bottom, right & left]   |            |
    |              |                                |            |
    |              | **With 3 float in the list :** |            |
    |              |                                |            |
    |              | [top, right & left, bottom]    |            |
    |              |                                |            |
    |              | **With 4 float in the list :** |            |
    |              |                                |            |
    |              | [top, right, bottom, left]     |            |
    +--------------+--------------------------------+------------+
    | rightborder  |                                | float      |
    +--------------+--------------------------------+------------+
    | leftborder   |                                | float      |
    +--------------+--------------------------------+------------+
    | topborder    |                                | float      |
    +--------------+--------------------------------+------------+
    | bottomborder |                                | float      |
    +--------------+--------------------------------+------------+
    """

    def __init__(self, **kwargs):
        PageAbstract.__init__(self)
        PageAbstract._quick_setup(self, kwargs)

    def toxml(self):
        """
        Returns page as LXML Element

        :returns: xml
        :rtype: lxml._Element
        """
        return PageAbstract.toxml(self, False)

    def fromxml(self, xml):
        """
        Set page attributes according to LXML Element

        :param xml: Page source as XML element
        :type xml: lxml._Element
        :returns: bool
        :rtype: bool
        """
        return PageAbstract.fromxml(self, xml, False)

    def fromdefault(self, default=False):
        """
        Set page attributes according to known defaults.

        :param default: Name of the set of defaults ("a4", "letter")
        :type default: str
        """
        PageAbstract.fromdefault(self, False, default)

    def set_orientation(self, orientation):
        """
        Set page orientation.

        :param orientation: "portrait" or "landscape"
        :type orientation: str
        :returns: bool
        :rtype: bool
        """
        return PageAbstract.set_orientation(self, orientation)


class MasterPage(PageAbstract):
    """
    Master page in SLA

    To add objects to this master page, use Document.append()

    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    +--------------+--------------------------------+------------+
    | Kwargs       | Setting                        | Value type |
    +==============+================================+============+
    | default      | Equivalent to a fromdefault    | boolean or |
    |              | call, value being the default  | string     |
    |              | name or True                   |            |
    +--------------+--------------------------------+------------+
    | posx         | X position of the page         | float      |
    +--------------+--------------------------------+------------+
    | posy         | Y position of the page         | float      |
    +--------------+--------------------------------+------------+
    | width        | Page width                     | float      |
    +--------------+--------------------------------+------------+
    | height       | Page height                    | float      |
    +--------------+--------------------------------+------------+
    | borders      | Shorthand for rightborder,     | List of    |
    |              | leftborder, topborder,         | floats     |
    |              | bottomborder.                  |            |
    |              |                                |            |
    |              | Read like the CSS margin       |            |
    |              | property:                      |            |
    |              |                                |            |
    |              | **With 1 float in the list :** |            |
    |              |                                |            |
    |              | [top & right & bottom & left]  |            |
    |              |                                |            |
    |              | **With 2 float in the list :** |            |
    |              |                                |            |
    |              | [top & bottom, right & left]   |            |
    |              |                                |            |
    |              | **With 3 float in the list :** |            |
    |              |                                |            |
    |              | [top, right & left, bottom]    |            |
    |              |                                |            |
    |              | **With 4 float in the list :** |            |
    |              |                                |            |
    |              | [top, right, bottom, left]     |            |
    +--------------+--------------------------------+------------+
    | rightborder  |                                | float      |
    +--------------+--------------------------------+------------+
    | leftborder   |                                | float      |
    +--------------+--------------------------------+------------+
    | topborder    |                                | float      |
    +--------------+--------------------------------+------------+
    | bottomborder |                                | float      |
    +--------------+--------------------------------+------------+
    """

    def __init__(self, **kwargs):
        PageAbstract.__init__(self)
        PageAbstract._quick_setup(self, kwargs)

    def toxml(self):
        """
        Returns master page object as LXML Element

        :returns: xml
        :rtype: lxml._Element
        """
        return PageAbstract.toxml(self, True)

    def fromxml(self, xml):
        """
        Set master page attributes according to LXML Element

        :param xml: Master page source as XML element
        :type xml: lxml._Element
        :returns: bool
        :rtype: bool
        """
        return PageAbstract.fromxml(self, xml, True)

    def fromdefault(self, default=False):
        """
        Set master page attributes according to known defaults.

        :param default: Name of the set of defaults ("a4", "letter")
        :type default: str
        """
        PageAbstract.fromdefault(self, True, default)

    def set_orientation(self, orientation):
        """
        Set master page orientation.

        :param orientation: "portrait" or "landscape"
        :type orientation: str
        :returns: bool
        :rtype: bool
        """
        return PageAbstract.set_orientation(self, orientation)


class PageSet(PyScribusElement):
    """
    Page set object.

    DOCUMENT/PageSets/Set
    """

    DEFAULTS = {
        "Single Page": {"first": 0, "rows": 1, "columns": 1, "names": []},
        "Facing Pages": {
            "first": 1, "rows": 1, "columns": 2,
            "names": ["Left Page", "Right Page"]
        },
        "3-Fold": {
            "first": 0, "rows": 1, "columns": 3,
            "names": ["Left Page", "Middle", "Right Page"]
        },
        "4-Fold": {
            "first": 0, "rows": 1, "columns": 4,
            "names": [
                "Left Page", "Middle Left", "Middle Right", "Right Page"
            ]
        }
    }

    def __init__(self):
        PyScribusElement.__init__(self)

        self.pyscribus_defaults = [k for k in PageSet.DEFAULTS.keys()]

        self.name = ""
        self.first_page = 0
        self.rows = 0
        self.columns = 0
        self.pages = []

    def fromdefault(self, default):
        """
        """

        if default in self.pyscribus_defaults:

            accurate = PageSet.DEFAULTS[default]

            self.name = default
            self.rows = accurate["rows"]
            self.pages = accurate["names"]
            self.columns = accurate["columns"]
            self.first_page = accurate["first"]

            return True
        else:
            return False

    def toxml(self):
        """
        :returns: xml
        :rtype: lxml._Element
        """

        xml = ET.Element("Set")

        #------------------------------------------------------

        xml.attrib["Name"] = self.name
        xml.attrib["FirstPage"] = str(self.first_page)
        xml.attrib["Rows"] = str(self.rows)
        xml.attrib["Columns"] = str(self.columns)

        #--- Page names ---------------------------------------

        if self.pages:

            for n in self.pages:

                pnx = ET.Element("PageNames")
                pnx.attrib["Name"] = n
                xml.append(pnx)

        #--- FIXME This exports undocumented attributes -------

        try:
            xml = undocumented_to_xml(xml, self.undocumented, no_none=True)
        except AttributeError:
            # NOTE If fromxml was not used
            pass

        return xml

    def fromxml(self, xml):
        """
        :param xml: Page set as XML element
        :type xml: lxml._Element
        :returns: bool
        :rtype: bool
        """

        if xml.tag == "Set":

            #------------------------------------------------------

            if (name := xml.get("Name")) is not None:
                self.name = name

            #------------------------------------------------------

            for att in ["FirstPage", "Rows", "Columns"]:

                if (atx := xml.get(att)) is not None:

                    try:
                        atx = int(atx)
                    except ValueError:
                        raise exception.InsaneSLAValue(
                            "Page set @{} must be a number.".format(
                                atx
                            )
                        )

            if (first := xml.get("FirstPage")) is not None:
                self.first_page = int(first)

            if (rows := xml.get("Rows")) is not None:
                self.rows = int(rows)

            if (columns := xml.get("Columns")) is not None:
                self.columns = int(columns)

            #--- Page names ---------------------------------------

            for child in xml:
                if child.tag == "PageNames":
                    n = child.get("Name")

                    if n not in self.pages:
                        self.pages.append(n)

            #--- FIXME This records undocumented attributes -------

            self.undocumented = undocumented_to_python(
                xml, ["GapBelow", "GapHorizontal", "GapVertical"]
            )

            return True
        else:
            return False

# vim:set shiftwidth=4 softtabstop=4 spl=en:
