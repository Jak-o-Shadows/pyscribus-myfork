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
PyScribus objects for… page objects manipulations.
"""

# Imports ===============================================================#

import copy
import math

import lxml
import lxml.etree as ET

import pyscribus.common.xml as xmlc
import pyscribus.exceptions as exceptions
import pyscribus.dimensions as dimensions
import pyscribus.itemattribute as itemattribute
import pyscribus.stories as stories

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

po_type_xml = {
    "image": 2,
    "text": 4,
    "line": 5,
    "polygon": 6,
    "polyline": 7,
    "textonpath": 8,
    "render": 9,
    "symbol": 11,
    "group": 12,
    "table": 16,
}

# Classes ===============================================================#

# NOTE PageObject est une classe obèse, mais il serait compliqué de gérer
# autrement les évolutions du SLA dans PyScribus

class PageObject(xmlc.PyScribusElement):
    """
    Page object in SLA (PAGEOBJECT)

    You should rather use TableObject, TextObject, TextOnPathObject,
    ImageObject, LineObject, PolylineObject, PolygonObject, RenderObject.

    :param ptype: Type of the PageObject. Must be in pageobjects.po_type_xml
        keys.
    :type ptype: str
    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance to link the page object to
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance to link the page object to

    :ivar string name: Human readable name

    .. seealso:: :class:`TableObject`, :class:`TextObject`,
        :class:`TextOnPathObject`, :class:`ImageObject`, :class:`LineObject`,
        :class:`PolylineObject`, :class:`PolygonObject`, :class:`RenderObject`
    """

    line_type_xml = {
        "solid": 1,
        "dashed": 2,
        "dotted": 3,
        "dash-dot": 4,
        "dash-dot-dot": 5
    }


    def __init__(
            self, ptype=False,
            sla_parent=False, doc_parent=False,
            **kwargs):

        global po_type_xml

        super().__init__()

        self.sla_parent = sla_parent
        self.doc_parent = doc_parent

        self.layer = 0
        self.name = ""

        self.attributes = []

        self.box = dimensions.DimBox()
        self.rotated_box = dimensions.DimBox()
        self.rotated = False

        self.have_stories = False
        self.on_master_page = False

        self.object_id = False

        # NOTE FIXME Implémenté car sinon plantage mais je comprends pas à
        # quoi sert cet attribut
        self.own_page = False

        self.linked = {"next": False, "previous": False}

        self.path = None
        self.copath = None

        if ptype:

            if ptype in po_type_xml.keys():
                self.ptype = ptype

                if ptype == "group":
                    self.group_objects = []

                elif ptype == "symbol":
                    self.pattern = None

                elif ptype == "text":
                    self.stories = []

                    self.columns = {
                        "gap": dimensions.Dim(0),
                        "count": 0
                    }

                    self.alignment = None

                elif ptype == "image":
                    # ImageData
                    self.data = ""
                    self.data_type = ""
                    # PFILE
                    self.filepath = ""

                elif ptype == "line":
                    self.line_type = "solid"

                    self.line_fill = "Black"
                    self.line_stroke = "Black"
                    self.line_thickness = dimensions.Dim(1)

                else:
                    self.ptype = None

        else:
            self.ptype = None

        if kwargs:
            self._quick_setup(kwargs)

    def fromxml(self, xml, arbitrary_tag=False):
        """
        :type xml: lxml._Element
        :param xml: XML source of the page object (PAGEOBJECT)
        :rtype: boolean
        :returns: True if XML parsing succeed
        """

        valid_tag = False

        if arbitrary_tag:
            if xml.tag == arbitrary_tag:
                valid_tag = True
        else:
            if xml.tag in ["PAGEOBJECT", "MASTEROBJECT"]:
                valid_tag = True

        if valid_tag:

            if xml.tag == "MASTEROBJECT":
                self.on_master_page = True

            # Page object attributes

            xml_name = xml.get("ANNAME")

            if xml_name is not None:
                self.name = xml_name
            else:
                self.name = ""

            own_id = xml.get("ItemID")

            if own_id is None:
                if self.name:
                    raise exceptions.MissingSLAAttribute(
                        "PAGEOBJECT '{}' must have @ItemID".format(self.name)
                    )
                else:
                    raise exceptions.MissingSLAAttribute(
                        "PAGEOBJECT must have @ItemID"
                    )
            else:
                self.object_id = own_id

            # --- Page object dimensions ---------------------------------

            xpos = xml.get("XPOS")
            ypos = xml.get("YPOS")
            width = xml.get("WIDTH")
            height = xml.get("HEIGHT")
            rotation = xml.get("ROT")

            valid_box = 0

            for test in [xpos, ypos, width, height]:
                if test is not None:
                    valid_box += 1

            if valid_box == 4:

                self.box.set_box(
                    top_lx=xpos,
                    top_ly=ypos,
                    width=width,
                    height=height
                )

                self.rotated_box = copy.deepcopy(self.box)

                if rotation is not None:

                    try:
                        rdegree = float(rotation)

                        if rdegree > 0:
                            self.rotated_box.rotate(rdegree)

                    except ValueError:
                        pass

            # --- Object path and copath ---------------------------------

            # NOTE FIXME Currently working for rectangular shapes

            for case in ["path", "copath"]:
                att = xml.get(case)

                if att is not None:

                    if self.ptype not in ["line", "polyline", "textonpath"]:
                        rectpath = RectPath()
                        success = rectpath.fromxml(att)

                        if success:
                            if case == "path":
                                self.path = rectpath
                            else:
                                self.copath = rectpath

            # --- Linked objects -----------------------------------------

            next_id = xml.get("NEXTITEM")
            prev_id = xml.get("BACKITEM")

            own_page = xml.get("OwnPage")

            for link_id in zip(["next", "previous"], [next_id, prev_id]):
                if link_id[1] is not None:
                    if link_id[1] == "-1":
                        self.linked[link_id[0]] = False
                    else:
                        self.linked[link_id[0]] = link_id[1]

            if own_page is not None:
                try:
                    if int(own_page):
                        self.own_page = int(own_page)
                    else:
                        self.own_page = False
                except ValueError:
                    raise exceptions.InsaneSLAValue(
                        "Invalid @OwnPage of PAGEOBJECT[@ItemID='{}']".format(
                            self.object_id
                        )
                    )

            # --- Layer of the page object -------------------------------

            layer = xml.get("LAYER")

            if layer is not None:

                try:
                    layer = int(layer)

                    if self.doc_parent:

                        if self.doc_parent.layers:

                            layer_found = False

                            for doc_layer in self.doc_parent.layers:

                                if layer == doc_layer.level:
                                    self.layer = layer
                                    layer_found = True
                                    break

                            if not layer_found:
                                raise exceptions.UnknownLayer(layer)

                except TypeError:
                    raise exceptions.InsaneSLAValue(
                        "PageObject @LAYER value should be an integer."
                    )

            # --- Image attribute ----------------------------------------

            if self.ptype == "image":
                idata = xml.get("ImageData")
                ipath = xml.get("PFILE")
                idata_ext = xml.get("inlineImageExt")

                if idata is not None and idata:
                    self.data = idata

                if idata_ext is not None and idata_ext:
                    self.data_type = idata_ext

                if ipath is not None and ipath:
                    self.filepath = ipath

            # --- Symbol attributes --------------------------------------

            if self.ptype == "symbol":
                pattern = xml.get("pattern")

                if pattern is not None:
                    self.pattern = pattern

            # --- Text attributes ----------------------------------------

            if self.ptype == "text":
                columns = xml.get("COLUMNS")
                columnsgap = xml.get("COLGAPS")
                alignment = xml.get("ALIGN")

                if columns is not None:
                    self.columns["count"] = int(columns)

                if columnsgap is not None:
                    self.columns["gap"].value = float(columnsgap)

                if alignment is not None:
                    for human, code in xmlc.alignment.items():
                        if alignment == code:
                            self.alignment = human
                            break

            # --- Line attributes ----------------------------------------

            if self.ptype == "line":
                fill = xml.get("PCOLOR")
                stroke = xml.get("PCOLOR2")
                thickness = xml.get("PWIDTH")
                line_type = xml.get("PLINEART")

                # TODO Walrus operator
                # if (line_type := xml.get("PLINEART") is not None:
                if line_type is not None:
                    for human, code in PageObject.line_type_xml.items():
                        if line_type == code:
                            self.line_type = human
                            break

                # TODO Walrus operator
                # if (fill := xml.get("PCOLOR") is not None:
                if fill is not None:
                    self.line_fill = fill

                # TODO Walrus operator
                # if (stroke := xml.get("PCOLOR2") is not None:
                if stroke is not None:
                    self.line_stroke = stroke

                # TODO Walrus operator
                # if (thickness := xml.get("PWIDTH") is not None:
                if thickness is not None:
                    self.line_thickness.value = float(thickness)

            # --- Text object attributes ---------------------------------

            if self.ptype == "text":
                cols = xml.get("COLUMNS")
                colsgap = xml.get("COLGAP")

                if cols is not None:
                    self.columns["count"] = int(cols)

                if colsgap is not None:
                    self.columns["gap"].value = float(colsgap)

            # ------------------------------------------------------------

            if self.ptype == "table":
                # Rows="4" Columns="3"

                # RowPositions="0 28.9378 57.8756 86.8134"
                # RowHeights="28.9378 28.9378 28.9378 28.9378"
                # ColumnPositions="0 48.0087 96.0174"
                # ColumnWidths="48.0087 48.0087 48.0087"

                rows = xml.get("Rows")
                cols = xml.get("Columns")

                # Les cellules sont listées de gauche à droite et de haut
                # en bas.

                rows_y = xml.get("RowPositions")
                # Hauteur (pas position)
                rows_h = xml.get("RowHeights")

                cols_x = xml.get("ColumnPositions")
                # Largeur (pas position)
                cols_w = xml.get("ColumnWidths")

                for posdim in [rows_y, rows_h, cols_x, cols_w]:
                    if posdim is not None:
                        posdim = [float(p.strip()) for p in posdim.split()]
                        print(posdim)

            # ------------------------------------------------------------

            # Page object childs

            if self.ptype == "group":

                for element in xml:

                    element_ptype = element.get("PTYPE")

                    if element_ptype is not None:

                        try:
                            po = new_from_type(
                                element_ptype, self.sla_parent,
                                self.doc_parent
                            )

                            success = po.fromxml(element)

                            if success:
                                self.group_objects.append(po)

                        except ValueError:
                            pass

            for element in xml:

                if self.ptype == "image":
                    # NOTE No childs in image object
                    pass

                if self.ptype == "text":

                    if element.tag == "PageItemAttributes":

                        for sub in element:

                            if sub.tag == "ItemAttribute":
                                iatt = itemattribute.PageObjectAttribute()
                                success = iatt.fromxml(sub)

                                if success:
                                    self.attributes.append(iatt)

                    if element.tag == "WeldEntry":
                        wo = WeldEntry()
                        success = wo.fromxml(element)

                        if wo:
                            # TODO FIXME Comment gérér les WeldEntry dans les
                            # instances PageObject ?
                            pass

                    if element.tag == "StoryText":
                        story = stories.Story()

                        story.sla_parent = self.sla_parent
                        story.doc_parent = self.doc_parent

                        success = story.fromxml(element)

                        if success:
                            if not self.stories:
                                self.have_stories = True

                            self.stories.append(story)

            #--- FIXME This records undocumented attributes --------------

            self.undocumented = xmlc.all_undocumented_to_python(xml)

            # ------------------------------------------------------------

            return True
        else:
            return False

    def toxml(self, arbitrary_tag=False):
        """
        :rtype: lxml._Element
        :returns: Page object as lxml._Element
        """

        global po_type_xml

        if arbitrary_tag:
            xml = ET.Element(arbitrary_tag)
        else:
            if self.on_master_page:
                xml = ET.Element("MASTEROBJECT")
            else:
                xml = ET.Element("PAGEOBJECT")

        xml.attrib["XPOS"] = self.box.coords["top-left"][0].toxmlstr()
        xml.attrib["YPOS"] = self.box.coords["top-left"][1].toxmlstr()
        xml.attrib["WIDTH"] = self.box.dims["width"].toxmlstr()
        xml.attrib["HEIGHT"] = self.box.dims["height"].toxmlstr()

        xml.attrib["ROT"] = self.rotated_box.rotation.toxmlstr()

        # NOTE ANNAME is optional
        if self.name is not None:
            if self.name:
                xml.attrib["ANNAME"] = self.name

        xml.attrib["ItemID"] = self.object_id

        # NOTE OwnPage doit exister quitte à juste être faux (= 0)
        # sinon plantage de Scribus.
        # wiki.scribus.net/canvas/(FR)_Introdution_au_Format_de_fichier_SLA_pour_Scribus_1.4

        xml.attrib["OwnPage"] = xmlc.bool_or_else_to_num(self.own_page)

        xml.attrib["PTYPE"] = str(po_type_xml[self.ptype])

        xml.attrib["LAYER"] = str(self.layer)

        # ------------------------------------------------------------

        if self.path is None:

            if self.ptype not in ["line", "polyline", "textonpath"]:
                # If the path for @path doesn't exist because this is a
                # object made from scratch and not through SLA parsing,
                # we make a rectangular path string on the fly, as
                # a wrong path is better than no path at all

                rectpath = RectPath()
                rectpath.frombox(self.box)

                xml.attrib["path"] = rectpath.toxmlstr()

        else:
            xml.attrib["path"] = self.path.toxmlstr()

        # ------------------------------------------------------------

        if self.ptype == "image":
            xml.attrib["ImageData"] = self.data
            xml.attrib["PFILE"] = self.filepath
            xml.attrib["inlineImageExt"] = self.data_type

        # ------------------------------------------------------------

        if self.ptype == "line":
            xml.attrib["PLINEART"] = str(PageObject.line_type_xml[self.line_type])
            xml.attrib["PCOLOR"] = self.line_fill
            xml.attrib["PCOLOR2"] = self.line_stroke
            xml.attrib["PWIDTH"] = self.line_thickness.toxmlstr()

        if self.ptype == "text":

            xml.attrib["COLUMNS"] = str(self.columns["count"])
            xml.attrib["COLGAPS"] = self.columns["gap"].toxmlstr()

            if self.alignment is not None:
                xml.attrib["ALIGN"] = xmlc.alignment[self.alignment]

            if self.have_stories:
                for story in self.stories:
                    sx = story.toxml()
                    xml.append(sx)

        # ------------------------------------------------------------

        # NOTE NEXTITEM contient le n° de l'item linké suivant (qui doit
        # exister sinon plantage de Scribus) ou -1
        # wiki.scribus.net/canvas/(FR)_Introdution_au_Format_de_fichier_SLA_pour_Scribus_1.4

        if self.linked["next"]:
            xml.attrib["NEXTITEM"] = self.linked["next"]
        else:
            xml.attrib["NEXTITEM"] = "-1"

        # NOTE BACKITEM contient le n° de l'item linké précédent (qui doit
        # exister sinon plantage de Scribus) ou -1
        # wiki.scribus.net/canvas/(FR)_Introdution_au_Format_de_fichier_SLA_pour_Scribus_1.4

        if self.linked["previous"]:
            xml.attrib["BACKITEM"] = self.linked["previous"]
        else:
            xml.attrib["BACKITEM"] = "-1"

        # TODO

        #--- FIXME This exports undocumented attributes -------

        try:
            # xml = undocumented_to_xml(xml, self.undocumented)
            xml, undoc_attribs = xmlc.all_undocumented_to_xml(
                xml, self.undocumented, True,
                self.ptype + "frame '" + self.name + "'"
            )

        except AttributeError:
            # NOTE If fromxml was not used
            pass

        return xml

    def has_attribute(self, name):
        for attribute in self.attributes:
            if attribute.name == name:
                return True

    def templatable(self):
        is_templatable = False

        if self.ptype != "text":
            attribute_pattern = self.sla_parent.templating["attribute-pattern"]

            for attribute in self.attributes:

                if attribute_pattern.search(attribute.name):
                    print(attribute)
                    is_templatable = True

        return False

    def copy(self, **kwargs):
        """
        Returns an independant copy of the page object instance.

        Use kwargs to quick set this copy as you made it.

        :type kwargs: dict
        :param kwargs: Quick setting (same as __init__)
        """

        duplicate = xmlc.PyScribusElement.copy(kwargs)

        if kwargs:
            duplicate._quick_setup(kwargs)

        return duplicate

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

                if setting_name == "posx":
                    self.box.coords["top-left"][0].value = float(setting_value)

                if setting_name == "posy":
                    self.box.coords["top-left"][1].value = float(setting_value)

                if setting_name == "width":
                    self.box.dims["width"].value = float(setting_value)

                if setting_name == "height":
                    self.box.dims["height"].value = float(setting_value)

                if setting_name == "layer":
                    self.layer = setting_value

                if self.ptype == "text":

                    if setting_name == "columns":
                        self.columns["count"] = int(setting_value)

                    if setting_name == "columnsgap":
                        self.columns["gap"].value = float(setting_value)

                if self.ptype == "image":

                    if setting_name == "filepath":
                        self.filepath = setting_value

                    if setting_name == "filedata":
                        self.data = setting_value

# Inherited from PageObject =============================================#

class TableObject(PageObject):
    """
    Table frame.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "table", sla_parent, doc_parent)
        PageObject._quick_setup(self, kwargs)


class GroupObject(PageObject):
    """
    Group of page objects.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    :ivar list group_objects: Page objects contained in this group.
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "group", sla_parent, doc_parent)
        PageObject._quick_setup(self, kwargs)


class SymbolObject(PageObject):
    """
    Symbol object.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "symbol", sla_parent, doc_parent)
        PageObject._quick_setup(self, kwargs)


class TextObject(PageObject):
    """
    Text frame object

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    +------------+-------------------------------+-----------+
    | Kwargs     | Setting                       | Type      |
    +============+===============================+===========+
    | default    | Equivalent to a fromdefault   | boolean   |
    |            | call, value being True or the | or string |
    |            | default name                  |           |
    +------------+-------------------------------+-----------+
    | columns    | Column count                  | integer   |
    +------------+-------------------------------+-----------+
    | columnsgap | Gap between each column       | float     |
    +------------+-------------------------------+-----------+
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "text", sla_parent, doc_parent)
        PageObject._quick_setup(self, kwargs)

    def fromdefault(self, default="with-story"):
        story = stories.Story()
        story.fromdefault()
        self.stories.append(story)
        self.have_stories = True

        self.columns = {
            "gap": dimensions.Dim(0),
            "count": 1
        }

    def templatable(self):
        stories = []

        if self.have_stories and self.stories:

            for story in self.stories:

                if story.templatable():

                    stories.append(story)

        return stories


class TextOnPathObject(PageObject):
    """
    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    def __init__(self, sla_parent=False, doc_parent=False):
        PageObject.__init__(self, "textonpath", sla_parent, doc_parent)


class ImageObject(PageObject):
    """
    Image frame object

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    +----------+-------------------------------+---------------+
    | Kwargs   | Setting                       | Type          |
    +==========+===============================+===============+
    | default  | Equivalent to a fromdefault   | boolean       |
    |          | call, value being True or the | or string     |
    |          | default name                  |               |
    +----------+-------------------------------+---------------+
    | filepath | Image filepath                | string        |
    +----------+-------------------------------+---------------+
    | filedata | Image data                    | Qt compressed |
    |          |                               | base64 string |
    +----------+-------------------------------+---------------+

    :ivar string filepath: File path of the image
    :ivar string data: Data if the incorporated image
    :ivar string data_type: Filetype of the incorporated image
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "image", sla_parent, doc_parent)
        PageObject._quick_setup(self, kwargs)


class LineObject(PageObject):
    """
    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    def __init__(self, sla_parent=False, doc_parent=False):
        PageObject.__init__(self, "line", sla_parent, doc_parent)


class PolylineObject(PageObject):
    """
    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    def __init__(self, sla_parent=False, doc_parent=False):
        PageObject.__init__(self, "polyline", sla_parent, doc_parent)


class PolygonObject(PageObject):
    """
    Polygon frame.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "polygon", sla_parent, doc_parent)
        PageObject._quick_setup(self, kwargs)


class RenderObject(PageObject):
    """
    LaTeX / render frame.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    def __init__(self, sla_parent=False, doc_parent=False):
        PageObject.__init__(self, "render", sla_parent, doc_parent)


class LatexObject(RenderObject):
    """
    Alias for RenderObject.

    LaTeX / render frame.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance

    .. seealso:: :class:`RenderObject`
    """

    def __init__(self, sla_parent=False, doc_parent=False):
        RenderObject.__init__(self, sla_parent, doc_parent)

# Render buffer and render properties ===================================#

class RenderBuffer(xmlc.PyScribusElement):
    """
    Object for render frame's (RenderObject) content.
    """

    def __init__(self):
        xmlc.PyScribusElement.__init__(self)

        self.properties = []
        self.content = ""

        self.dpi = dimensions.Dim(0, "dpi")
        self.use_preamble = False
        self.configfile = ""

    def fromdefault(self):
        """
        Sets a default RenderBuffer.

        - Font size is 11pt
        - LaTeX additional headers contains amsmath package.
        - DPI is 300 (standard DPI for print)
        """

        headers = HeadersRenderProperty(value="")
        headers.append_package("amsmath")

        self.properties = [
            headers,
            RenderProperty("font", ""),
            RenderProperty("fontsize", "11pt"),
        ]

        # NOTE Standard printing DPI
        self.dpi.value = 300

    def has_package(self, name):
        """
        Check if package name exists in the LaTeX preamble.

        :type name: str
        :param name: Name of the package
        :rtype: boolean
        :returns: True if the package exists
        :raise pyscribus.exceptions.UnknownRenderBufferProperty: If the LaTeX 
            preamble property (HeadersRenderProperty) doesn't exists.
        """
        for prop in properties:

            if isinstance(prop, HeadersRenderProperty):
                return prop.has_package(name)

        raise exceptions.UnknownRenderBufferProperty(
            "Property additionalheaders doesn't exists in render buffer object."
        )

    def append_package(self, name, options=""):
        """
        Append a package in the LaTeX preamble.

        :type name: str
        :param name: Name of the package
        :type options: str
        :param options: Package's options
        :rtype: boolean
        :returns: True if package appending succeed

        ..note:: As LaTeX additional headers is managed with 
            pageobjects.HeadersRenderProperty, it is better to use this 
            method than editing RenderBuffer.properties.

        Example:

          render_buffer.append_package("csquotes", "strict=true")

          is the equivalent of :

          \\usepackage[strict=true]{csquotes}
        """

        for prop in properties:

            if isinstance(prop, HeadersRenderProperty):
                prop.append_package(name, options)

                return True

        return False

    def set_fontsize(self, fontsize):
        """
        Set the font size of the render buffer content.

        :type fontsize: float, int
        :param fontsize: Font size in points

        .. note:: As fontsize is a standard render frame property, it is better
            to use this method than editing RenderBuffer.properties.
        """

        for prop in self.properties:

            if prop.name == "fontsize":
                prop.raw_value = "{}pt".format(float(fontsize))

                return True

        self.properties.append(
            RenderProperty("fontsize", float(fontsize))
        )

        return True

    def fromxml(self, xml):
        """
        :rtype: boolean
        :returns: True if XML parsing succeed
        """

        if xml.tag == "LATEX":
            # Attributes

            dpi = xml.get("DPI")

            if dpi is not None:
                self.dpi.value = float(dpi)

            use_preamble = xml.get("USE_PREAMBLE")

            if use_preamble is not None:
                self.use_preamble = xmlc.num_to_bool(use_preamble)

            configfile = xml.get("ConfigFile")

            if configfile is not None:
                self.configfile = configfile

            # Properties

            for element in xml:

                if element.tag == "PROPERTY":

                    if "name" in element.attrib:

                        if element.attrib["name"] == "additionalheaders":
                            po = HeadersRenderProperty()
                        else:
                            po = RenderProperty()

                    else:
                        po = False

                    if po:
                        success = po.fromxml(element)

                        if success:
                            self.properties.append(po)

            # TODO Content

            return True
        else:
            return False

    def toxml(self):
        xml = ET.Element("LATEX")

        xml.attrib["ConfigFile"] = self.configfile
        xml.attrib["DPI"] = self.dpi.toxmlstr()
        xml.attrib["USE_PREAMBLE"] = xmlc.bool_to_num(self.use_preamble)

        for prop in self.properties:
            px = prop.toxml()
            xml.append(px)

        xml.text = self.content

        return xml

class RenderProperty(xmlc.PyScribusElement):
    """
    Render frame / object property in SLA.

    :type name: str
    :param name: Name of the property
    :type value: str
    :param value: Value of the property

    .. note:: If you want to change the property value type, use 
        RenderProperty.value. RenderProperty.raw_value keep property 
        value as it was at instanciation.

    .. note:: Use HeadersRenderProperty if your property name is "additionalheaders".

    .. seealso:: :class:`HeadersRenderProperty`
    """

    def __init__(self, name="", value=False):
        xmlc.PyScribusElement.__init__(self)

        self.name = name
        self._set_value(value)

    def _set_value(self, value):
        self.raw_value = value
        self.value = copy.deepcopy(value)

    def fromxml(self, xml):
        """
        Define render property from lxml element.

        :type xml: lxml._Element
        :param xml: Render property as lxml._Element
        :rtype: boolean
        :returns: True if XML parsing succeed
        """

        if xml.tag == "PROPERTY":
            name = xml.get("name")
            value = xml.get("value")

            if name is not None:
                self.name = name

            if value is not None:
                self._set_value(value)

            return True
        else:
            return False

    def toxml(self):
        """
        :returns: lxml._Element representation of render frame property
        :rtype: lxml._Element
        """
        xml = ET.Element("PROPERTY")
        xml.attrib["name"] = self.name
        xml.attrib["value"] = self.raw_value

        return xml

class HeadersRenderProperty(RenderProperty):
    """
    Render frame / object property in SLA for LaTeX preamble.

    :type value: str
    :param value: Value of the property

    .. note:: HeadersRenderProperty property name is always additionalheaders.

    .. seealso:: :class:`RenderProperty`
    """

    def __init__(self, value=False):
        RenderProperty.__init__(self, "additionalheaders", value)

        self.packages = []

        if value:
            self.packages = value.split("&#10;")

    def fromxml(self, xml):
        success = RenderProperty.fromxml(self, xml)

        if success:
            self.packages = self.value.split("&#10;")

        return success

    def has_package(self, name):
        """
        Check if package name exists in the LaTeX preamble.

        :type name: str
        :param name: Name of the package
        :rtype: boolean
        :returns: True if the package exists
        """

        for package in self.packages:
            pn = package.split("{")[-1].split("}")[0]

            if pn == name:
                return True

        return False

    def append_package(self, name, options=""):
        """
        Append a package in the LaTeX preamble.

        :type name: str
        :param name: Name of the package
        :type options: str
        :param options: Package's options
        :rtype: boolean
        :returns: True if package appending succeed
        """

        ps = "\\" + "usepackage"

        if options:
            ps += "[{}]".format(options)

        ps += "{" + name + "}"

        if ps not in self.packages:
            self.packages.append(ps)

        return True

    def toxml(self):
        xml = RenderProperty.toxml(self)

        # NOTE Override value attributes with packages
        xml.attrib["value"] = "&#10;".join(self.packages)

        return xml


class WeldEntry(xmlc.PyScribusElement):

    def __init__(self):
        xmlc.PyScribusElement.__init__(self)

        self.target = False
        # TODO Savoir si c’est des Dim
        self.coords = {"x": 0, "y": 0}

    def fromxml(self, xml):
        if xml.tag == "WeldEntry":
            target = xml.get("Target")
            wx,wy = xml.get("WX"),xml.get("WY")

            if target is not None:
                # TODO FIXME Il faudrait vérifier qu’un objet avec cet ID
                # existe, mais généralement, il est à la suite, donc hors
                # de ce qui constitue encore le document lors du parsing
                self.target = target

            return True
        else:
            return False

    def toxml(self):
        xml = ET.Element("WeldEntry")
        # TODO Savoir si c’est des Dim
        xml["WX"] = str(self.coords["x"])
        xml["WY"] = str(self.coords["y"])

        return xml

    def fromdefault(self):
        # TODO Savoir si c’est des Dim
        self.coords = {"x": 0, "y": 0}
        self.target = False

# Paths =================================================================#

class RectPath:
    """
    Path object for easiest manipulation of @path / @copath of rectangular
    shapes.

    Translate strings like :

    M0 0 L515.276 0 L515.276 761.89 L0 761.89 L0 0 Z

    Into a list of PathPoint instances.
    """

    def __init__(self):
        self.raw = None
        self.points = []

    def add_point(self, x, y):
        existing = [p for p in self.points if p.x == x and p.y == y]

        if not existing:
            new_point = PathPoint(x, y, fromsla=False)

            self.points.append(new_point)

            return True

        return False

    def fromxml(self, xmlstring):
        # Reset of points list
        self.points = []
        # Temporary list of points
        points = []

        # We save the original string
        self.raw = xmlstring

        #--- Extracting the points ----------------------------------

        splitted = xmlstring.split()

        is_point = False
        current_point = []

        for element in splitted:

            if is_point:
                current_point.append(element)
                points.append(current_point)
                current_point = []
                is_point = False

            if element.startswith("L"):
                is_point = True
                current_point.append(element)

        #--- Points processing --------------------------------------

        for point in points:
            x = float(point[0][1:])
            y = float(point[1])

            px = PathPoint(x, y, fromsla=True)

            self.points.append(px)

        #--- Export in XML check ------------------------------------

        restored = self.toxmlstr()

        if self.raw != restored:
            print("--------------------------------")
            print("Unable to restore points of path")
            print("Original path :", self.raw)
            print("Restored path :", restored)

        #------------------------------------------------------------

        return True

    def frombox(self, box):
        """
        Set the points from a DimBox.

        :type box: pyscribus.dimensions.DimBox
        :param box: Box of a page, page object
        :rtype: boolean
        :returns: True if point setting succeed.
        """

        # Reset of points list
        self.points = []

        # Getting width and height
        width = box.dims["width"].value
        height = box.dims["height"].value

        #--- Making the four points of the rectangle ----------------

        tr = PathPoint(width, 0) # Top-right
        br = PathPoint(width, height) # Bottom-right
        bl = PathPoint(0, height) # Bottom-left
        tl = PathPoint(0, 0) # Top-Left / Origin point

        #--- Adding the points clockwise ----------------------------

        for point in [tr, br, bl, tl]:
            self.points.append(point)

        return True

    def toxml(self):
        """Alias of toxmlstr"""

        return self.toxmlstr()

    def toxmlstr(self):
        if self.points:
            xml = "M0 0 "

            #------------------------------------------------------------
            # Sorting the points and making 3 sets of them to make sure
            # they are added to XML string clockwise, the origin point
            # being the last one

            with_x = sorted(
                [p for p in self.points if p.x > 0],
                key=lambda p: p.x
            )

            with_y = sorted(
                [p for p in self.points if p.x == 0 and p.y > 0],
                key=lambda p: p.x, reverse=True
            )

            try:
                origin = [p for p in self.points if p.is_origin()][0]
            except IndexError:
                # When RectPath is used in polyline objects which are
                # without origin points as RectPath defines it
                origin = []

            #------------------------------------------------------------

            xml += " ".join([i.toxmlstr() for i in with_x]) + " "
            xml += " ".join([i.toxmlstr() for i in with_y]) + " "

            try:
                xml += origin.toxmlstr() + " "
            except AttributeError:
                # Idem
                pass

            xml += "Z"

            return xml

        else:
            return False

class PathPoint:

    def __init__(self, x=0, y=0, fromsla=False):

        if fromsla:
            self.x = x
            self.y = y
        else:
            self.x = self._round_coord(x)
            self.y = self._round_coord(y)

    def _round_coord(self, n):
        """
        Round up the float n to the third decimal.
        """
        return math.ceil(n * 1000) / 1000

    def is_origin(self):
        if self.x == float(0) and self.y == float(0):
            return True
        else:
            return False

    def toxmlstr(self):
        if float(self.x) == int(self.x):
            x = int(self.x)
        else:
            x = self.x

        if float(self.y) == int(self.y):
            y = int(self.y)
        else:
            y = self.y

        return "L{} {}".format(x, y)

    def __repr__(self):
        return self.toxmlstr()

# Variables globales 2 ==================================================#

po_type_classes = {
    "image": ImageObject,
    "text": TextObject,
    "line": LineObject,
    "polygon": PolygonObject,
    "polyline": PolylineObject,
    "textonpath": TextOnPathObject,
    "render": RenderObject,
    "table": TableObject,
    "group": GroupObject,
    "symbol": SymbolObject
}

# Fonctions =============================================================#

# NOTE This function to avoid document module managing page objects
# classes selections. We just need to modify po_type_xml, po_type_classes
# and PageObject class to extend page object valid types.

def new_from_type(ptype, sla_parent=False, doc_parent=False, **kwargs):
    """
    Returns an instance of the correct class of page object according
    to ptype value.

    Although it is not a good idea for readability, you can make new
    page objects only with new_from_type() instead of instanciating
    the appropriate class of page object.

    :type ptype: str
    :param ptype: SLA @PTYPE attribute value or "human readable"
        value in pageobjects.po_type_xml keys.
    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance to link the page object to
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance to link the page object to
    :type kwargs: dict
    :param kwargs: Page object quick setting (see kwargs table of the
        matching class)
    """

    global po_type_xml
    global po_type_classes

    # --- Finding the matching page object name -------------------------------

    vtype = False
    ptype = ptype.lower()

    if ptype in po_type_xml:
        # If ptype is already the human equivalent of SLA @PTYPE
        vtype = ptype

    else:
        # If ptype is SLA @PTYPE

        # NOTE latex as render alias
        if ptype == "latex":
            vtype = "render"

        else:
            for human, xml in po_type_xml.items():
                if str(xml) == ptype:
                    vtype = human
                    break

    # --- Creating the new page object ----------------------------------------

    if vtype:
        po = po_type_classes[vtype]()
        po.ptype = vtype

        # Page object quick setup
        if kwargs:
            po._quick_setup(kwargs)

        if sla_parent:
            po.sla_parent = sla_parent

        if doc_parent:
            po.doc_parent = doc_parent

        return po

    else:
        raise ValueError(
            "Invalid ptype for pageobjects.from_pageobject_type(): {}".format(
                ptype
            )
        )

    # -------------------------------------------------------------------------

# vim:set shiftwidth=4 softtabstop=4 spl=en:
