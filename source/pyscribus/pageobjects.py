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
import pyscribus.styles as pstyles

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

    shape_type_xml = {
        "rectangle": "0",
        "ellipse": "1",
        "rounded-rectangle": "2",
        "free": "3",
    }

    def __init__(
            self, ptype=False,
            sla_parent=False, doc_parent=False,
            **kwargs):

        global po_type_xml

        super().__init__()

        # --- Page object parents ------------------------------------

        self.sla_parent = sla_parent
        self.doc_parent = doc_parent

        # --- --------------------------------------------------------

        self.name = ""
        self.layer = 0
        self.attributes = []

        # --- Page object shape and boxes ----------------------------

        self.box = dimensions.DimBox()
        self.rotated_box = dimensions.DimBox()
        self.rotated = False
        self.shape = {"type": None, "edited": None}

        # --- Page object own_page and linking/id --------------------

        # NOTE FIXME Implemented because without it Scribus crashes, but
        #            I don't understand the meaning of this attribute.
        self.own_page = False

        self.object_id = False

        self.linked = {"next": None, "previous": None}

        # --- --------------------------------------------------------

        self.on_master_page = False
        self.have_stories = False

        # --- Page object paths --------------------------------------

        self.path = None
        self.copath = None

        # --- --------------------------------------------------------

        if ptype and ptype in po_type_xml.keys():
            self.ptype = ptype
        else:
            self.ptype = None

        # --- Quick setup --------------------------------------------

        if kwargs:
            self._quick_setup(kwargs)

    def fromdefault(self):
        self.shape = {"type": "rectangle", "edited": False}

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

            if (xml_name := xml.get("ANNAME")) is not None:
                self.name = xml_name
            else:
                self.name = ""

            if (own_id := xml.get("ItemID")) is None:
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
                        else:
                            self.rotated_box.rotation.value = 0

                    except ValueError:
                        pass

            # --- Object path, copath and shape --------------------------

            if (editedshape := xml.get("CLIPEDIT")) is not None:
                self.shape["edited"] = xmlc.num_to_bool(editedshape)

            if (shapetype := xml.get("FRTYPE")) is not None:

                for human,code in PageObject.shape_type_xml.items():
                    if shapetype == code:
                        self.shape["type"] = human
                        break

            # NOTE FIXME Currently only working for rectangular shapes

            for case in ["path", "copath"]:

                if (att := xml.get(case)) is not None:

                    if self.ptype not in ["line", "polyline", "textonpath"]:
                        rectpath = RectPath()

                        if (success := rectpath.fromxml(att)):
                            if case == "path":
                                self.path = rectpath
                            else:
                                self.copath = rectpath

            # --- Linked objects -----------------------------------------

            next_id = xml.get("NEXTITEM")
            prev_id = xml.get("BACKITEM")

            for link_id in zip(["next", "previous"], [next_id, prev_id]):

                if link_id[1] is not None:
                    if link_id[1] == "-1":
                        self.linked[link_id[0]] = None
                    else:
                        self.linked[link_id[0]] = link_id[1]

            if (own_page := xml.get("OwnPage")) is not None:
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

            if (layer := xml.get("LAYER")) is not None:

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

            # --- Type specific attributes -------------------------------
            # Moved to ImageObject
            # Moved to TextObject
            # Moved to LineObject
            # Moved to TableObject

            # --- Symbol attributes --------------------------------------

            if self.ptype == "symbol":

                if (pattern := xml.get("pattern")) is not None:
                    self.pattern = pattern


            # --- Text object attributes ---------------------------------

            # FIXME FIXME FIXME Gné ? C’est déjà dans TextObject
            if self.ptype == "text":
                colsgap = xml.get("COLGAP")

                if colsgap is not None:
                    self.columns["gap"].value = float(colsgap)

            # --- Page objects specific children -------------------------
            # Moved in TableObject
            # Moved in TableObject
            # Moved in TableObject
            # NOTE No childs in image object

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

        xml.attrib["ROT"] = self.rotated_box.rotation.toxmlstr(True)

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

        if self.shape["type"] is None:
            # If the shape type is not defined, we assume the frame has
            # a rectangular shape, as it is the most common
            xml.attrib["FRTYPE"] = PageObject.shape_type_xml["rectangle"]
        else:
            xml.attrib["FRTYPE"] = PageObject.shape_type_xml[self.shape["type"]]

        if self.shape["edited"] is None:
            xml.attrib["CLIPEDIT"] = "0"
        else:
            xml.attrib["CLIPEDIT"] = xmlc.bool_to_num(self.shape["edited"])

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

        # --- Previous / Next item -----------------------------------

        # NOTE @NEXTITEM must be the @ItemID of the next EXISTING item
        #      (if the item doesn't exists, Scribus crashes), or -1

        if self.linked["next"] is None:
            xml.attrib["NEXTITEM"] = "-1"
        else:
            xml.attrib["NEXTITEM"] = self.linked["next"]

        # NOTE @BACKITEM must be the @ItemID of the next EXISTING item
        #      (if the item doesn't exists, Scribus crashes), or -1

        if self.linked["previous"] is None:
            xml.attrib["BACKITEM"] = "-1"
        else:
            xml.attrib["BACKITEM"] = self.linked["previous"]

        #--- FIXME This exports undocumented attributes -------

        if self.ptype not in ["table"]:

            try:
                xml, undoc_attribs = xmlc.all_undocumented_to_xml(
                    xml, self.undocumented, True,
                    self.ptype + " frame '" + self.name + "'"
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
        Method for defining page object settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            xmlc.PyScribusElement._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                if setting_name == "posx":
                    self.box.setx("top-left", float(setting_value))

                if setting_name == "posy":
                    self.box.sety("top-left", float(setting_value))

                if setting_name == "width":
                    self.box.dims["width"].value = float(setting_value)

                if setting_name == "height":
                    self.box.dims["height"].value = float(setting_value)

                if setting_name == "layer":
                    self.layer = setting_value

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

    :ivar list cells: Table cells (TableCell instances)
    :ivar integer rows: Number of rows
    :ivar integer columns: Number of columns
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "table", sla_parent, doc_parent)

        #--- Specific attributes to this subclass ------------------------

        self.rows = 0
        self.columns = 0

        self.cells = []

        self.style = None

        self.fill = {"color": "None", "shade": None}

        self.borders = {
            "left": None, "right": None,
            "top": None, "bottom": None
        }

        #--- Then, quick setup -------------------------------------------

        PageObject._quick_setup(self, kwargs)

    #--- Cells update methods -----------------------------------------------

    def _update_rowcols_count(self):
        """Update the count of rows and columns."""

        self.rows = max([cell.row for cell in self.cells]) + 1
        self.columns = max([cell.column for cell in self.cells]) + 1

    def _update_cells_geometry(self, cols, rows):
        """
        Set each cell box according its row's position & height and its
        column's position and width.
        """

        colsdict,rowsdict = {},{}

        for col in cols:
            col_index,col_x,col_width = col
            colsdict[col_index] = {"position": col_x, "width": col_width}

        for row in rows:
            row_index,row_y,row_height = row
            rowsdict[row_index] = {"position": row_y, "height": row_height}

        for cell in self.cells:
            row = rowsdict[cell.row]
            column = colsdict[cell.column]

            cell.box.set_box(
                top_lx=column["position"],
                top_ly=row["position"],
                width=column["width"],
                height=row["height"]
            )

    #--- --------------------------------------------------------------------

    def _append_row_at_end(self, height=False):
        """
        Append a row at the end of the table.

        :type height: boolean,float
        :param height: Height of the new rows
        :rtype: list
        :returns: List of new cells
        """

        self._update_rowcols_count()

        # --- Getting columns informations ---------------------------

        columns = {}

        for cell in self.cells:

            if cell.column not in columns:
                columns[cell.column] = {
                    # "x": float(cell.box.coords["top-left"][0]),
                    "x": float(cell.box.getx("top-left")),
                    "width": float(cell.box.dims["width"]),
                    "borders": cell.borders, "padding": cell.padding,
                    "fill": cell.fill, "align": cell.align,
                    "style": cell.style
                }

        # --- Getting the last row y and height ----------------------

        last_y,last_height = None,None

        for cell in self.cells:

            if cell.row == (self.rows - 1):
                # last_y = float(cell.box.coords["top-left"][1])
                last_y = float(cell.box.gety("top-left"))
                last_height = float(cell.box.dims["height"])

                break

        # --- Adding the new row -------------------------------------

        if last_y is not None and last_height is not None:

            new_y = last_y + last_height

            if height:
                new_height = float(height)
            else:
                new_height = last_height

            self.box.dims["height"] += float(new_height)

            # --- Adding the cell in each column of the new row ------

            new_cells = []

            for column_index, datas in columns.items():
                cell = TableCell(
                    self, default=True,
                    column = column_index, row = self.rows,
                    posx=datas["x"], posy=new_y,
                    width=datas["width"], height=new_height,
                    fillcolor=datas["fill"]["color"],
                    fillshade=datas["fill"]["shade"],
                    padding=datas["padding"], borders=datas["borders"],
                    alignment=datas["align"], style=datas["style"],
                )

                self.cells.append(cell)
                new_cells.append(self.cells[-1])

            self._update_rowcols_count()

            return new_cells

        # ------------------------------------------------------------

        return False

    def append_row(self, height=False, position=-1):
        """
        Append a row at the end of the table.

        :type height: boolean,float
        :param height: Height of the new row
        :param position: The row is appended after the 
            position-n row. If -1, the row is appended 
            after the last row of the table.
        :rtype: list
        :returns: List of new cells
        """

        self._update_rowcols_count()

        # --- If position is -1 = end of the table -------------------

        if position < 0:
            return self._append_row_at_end(height)

        # --- If position is not at the end of the table -------------

        if position != -1:

            # --- Getting columns informations ---------------------------

            columns = {}

            for cell in self.cells:

                if cell.column not in columns:
                    columns[cell.column] = {
                        # "x": float(cell.box.coords["top-left"][0]),
                        "x": float(cell.box.getx("top-left")),
                        "width": float(cell.box.dims["width"]),
                        "borders": cell.borders, "padding": cell.padding,
                        "fill": cell.fill, "align": cell.align,
                        "style": cell.style
                    }

            # --- Getting the y and height of the row matching position --

            index_row_y,index_row_height = None,None

            for cell in self.cells:

                if cell.row == position - 1:
                    # index_row_y = float(cell.box.coords["top-left"][1])
                    index_row_y = float(cell.box.gety("top-left"))
                    index_row_height = float(cell.box.dims["height"])

                    break

            # --- Adding the new row -------------------------------------

            if index_row_y is not None and index_row_height is not None:

                # Getting the Y of the new row
                new_y = index_row_y + index_row_height

                # Setting the height of the new row
                if height:
                    new_height = float(height)
                else:
                    new_height = index_row_height

                # Adjust the table box with the height of the new row
                self.box.dims["height"] += float(new_height)

                # --------------------------------------------------------

                # Update the coordinates and col/rows positions of the 
                # rows < position & rows > position

                for cell in self.cells:

                    if cell.row < (position - 1):
                        cell.row -= 1
                        cell.box.coords["top-left"][1].value -= new_height
                        continue

                    if cell.row > (position + 1):
                        cell.row += 1
                        cell.box.coords["top-left"][1].value += new_height
                        continue

                # --- Adding the cell in each column of the new row ------

                new_cells = []

                for column_index, datas in columns.items():
                    cell = TableCell(
                        self, default=True,
                        column = column_index, row = position,
                        posx=datas["x"], posy=new_y,
                        width=datas["width"], height=new_height,
                        fillcolor=datas["fill"]["color"],
                        fillshade=datas["fill"]["shade"],
                        padding=datas["padding"], borders=datas["borders"],
                        alignment=datas["align"], style=datas["style"],
                    )

                    self.cells.append(cell)
                    new_cells.append(self.cells[-1])

                # --------------------------------------------------------

                self._update_rowcols_count()

                return new_cells

            # ------------------------------------------------------------

            return False

        return False

    def append_rows(self, number=1, height=False, position=-1):
        """
        Append rows at the end of the table.

        :type number: integer
        :param number: Number of colums to append
        :type height: boolean,float
        :param height: Height of the new rows
        :type position: integer
        :param position: The rows are appended 
            after the position-n row. If -1, the
            rows are appended after the last 
            row of the table.
        :rtype: list
        :returns: List of new cells by rows
        """

        new_cells,added = [],0

        if position == -1:
            at_end = True
        else:
            at_end = False
            row_index = position

        for add in range(number):

            if at_end:
                cells = self.append_row(height)
            else:
                cells = self.append_row(height, row_index)
                row_index += 1

            if cells:
                added += 1
                new_cells.append(cells)

        if added == number:
            return True
        else:
            return False

    def append_column(self, width=False):
        """
        Append a column at the end of the table.

        :type width: boolean,float
        :param width: Width of the new column
        :rtype: list
        :returns: List of new cells
        """

        self._update_rowcols_count()

        # --- Getting rows informations ------------------------------

        rows = {}

        for cell in self.cells:

            if cell.row not in rows:
                rows[cell.row] = {
                    # "y": float(cell.box.coords["top-left"][1]),
                    "y": float(cell.box.gety("top-left")),
                    "height": float(cell.box.dims["height"]),
                    "borders": cell.borders, "padding": cell.padding,
                    "fill": cell.fill, "align": cell.align,
                    "style": cell.style
                }

        # --- Getting the last column x and width --------------------

        last_x,last_width = None,None

        for cell in self.cells:

            if cell.column == (self.columns - 1):
                # last_x = float(cell.box.coords["top-left"][0])
                last_x = float(cell.box.getx("top-left"))
                last_width = float(cell.box.dims["width"])

                break

        # --- Adding the new column ----------------------------------

        if last_x is not None and last_width is not None:

            # Getting the X of the new column
            new_x = last_x + last_width

            # Setting the width of the new column
            if width:
                new_width = float(width)
            else:
                new_width = last_width

            # Adjust the table box with the width of the new row
            self.box.dims["width"] += float(new_width)

            # --- Adding the cell in each row of the new column ------

            new_cells = []

            for row_index, datas in rows.items():
                cell = TableCell(
                    self, default=True,
                    column = self.columns, row = row_index,
                    posx=new_x, posy=datas["y"],
                    width=new_width, height=datas["height"],
                    fillcolor=datas["fill"]["color"],
                    fillshade=datas["fill"]["shade"],
                    padding=datas["padding"], borders=datas["borders"],
                    alignment=datas["align"], style=datas["style"],
                )

                self.cells.append(cell)
                new_cells.append(self.cells[-1])

            self._update_rowcols_count()

            return new_cells

        # ------------------------------------------------------------

        return False

    def append_columns(self, number=1, width=False):
        """
        Append columns at the end of the table.

        :type number: integer
        :param number: Number of colums to append
        :type width: boolean,float
        :param width: Width of the new columns
        :rtype: list
        :returns: List of new cells by columns
        """

        new_cells,added = [],0

        for add in range(number):
            cells = self.append_column(width)

            if cells:
                added += 1
                new_cells.append(cells)

        if added == number:
            return True
        else:
            return False

    #--- PyScribus standard methods -----------------------------------------

    def toxml(self):
        """
        :rtype: lxml._Element
        :returns: Table object as LXML element
        """

        xml = PageObject.toxml(self)

        if isinstance(xml, ET._Element):
            # --- Attributes ---------------------------------------------

            self._update_rowcols_count()

            # Number of rows and columns ----------------------------

            if self.rows > 0:
                xml.attrib["Rows"] = str(self.rows)
            else:
                raise ValueError("Table object has zero rows.")

            if self.columns > 0:
                xml.attrib["Columns"] = str(self.columns)
            else:
                raise ValueError("Table object has zero columns.")

            # Columns and rows datas --------------------------------

            rowsh,colsw = {},{}
            rowsp,colsp = {},{}

            for cell in self.cells:

                if cell.row not in rowsh:
                    rowsh[cell.row] = cell.box.dims["height"].toxmlstr(True)

                if cell.row not in rowsp:
                    rowsp[cell.row] = cell.box.coords["top-left"][1].toxmlstr(True)

                if cell.column not in colsw:
                    colsw[cell.column] = cell.box.dims["width"].toxmlstr(True)

                if cell.column not in colsp:
                    colsp[cell.column] = cell.box.coords["top-left"][0].toxmlstr(True)

            for case in [
                    ["RowPositions", rowsp], ["RowHeights", rowsh],
                    ["ColumnPositions", colsp], ["ColumnWidths", colsw]]:

                xml.attrib[case[0]] = " ".join(
                    case[1][n] for n in sorted(case[1].keys())
                )

            #--- FIXME This exports undocumented attributes --------------

            try:
                xml, undoc_attribs = xmlc.all_undocumented_to_xml(
                    xml, self.undocumented, True,
                    self.ptype + " frame '" + self.name + "'"
                )

            except AttributeError:
                # NOTE If fromxml was not used
                pass

            # --- Children -----------------------------------------------

            # TableData attributes

            tabdata = ET.Element("TableData")

            if self.style is None:
                tabdata.attrib["Style"] = ""
            else:
                tabdata.attrib["Style"] = self.style

            tabdata.attrib["FillColor"] = self.fill["color"]

            if self.fill["shade"] is None:
                tabdata.attrib["FillShade"] = "100"
            else:
                tabdata.attrib["FillShade"] = self.fill["shade"].toxmlstr(True)

            # TableData children

            for side in ["left", "right", "top", "bottom"]:

                if self.borders[side] is not None:
                    bx = self.borders[side].toxml()
                    tabdata.append(bx)

            for cell in self.cells:
                cx = cell.toxml()
                tabdata.append(cx)

            # Adding TableData as xml child
            xml.append(tabdata)

            return xml

        return False

    def fromxml(self, xml):
        succeed = PageObject.fromxml(self, xml)

        if succeed:

            # --- Attributes ---------------------------------------------

            # Number of rows and columns

            if (rows := xml.get("Rows")) is not None:
                self.rows = int(rows)

            if (cols := xml.get("Columns")) is not None:
                self.columns = int(cols)

            # Rows and columns widths and heights -------------------

            # Getting rows datas -------------------------------

            # Y position of the row, with the top-left corner
            # of the first cell of the first row is at 0

            if (row_y := xml.get("RowPositions")) is not None:
                row_y = [float(i) for i in row_y.split()]

            # Height (dimension, not position)

            if (row_h := xml.get("RowHeights")) is not None:
                row_h = [float(i) for i in row_h.split()]

            # Getting columns datas ----------------------------

            # X position of the column, with the top-left corner
            # of the first cell of the first row is at 0

            if (col_x := xml.get("ColumnPositions")) is not None:
                col_x = [float(i) for i in col_x.split()]

            # Width (dimension, not position)

            if (col_w := xml.get("ColumnWidths")) is not None:
                col_w = [float(i) for i in col_w.split()]

            # Mixing datas together ----------------------------
            # cols datas: index, X, width
            # rows dataa: index, Y, height

            cols_datas = [
                i for i in zip([x for x in range(len(col_x))], col_x, col_w)
            ]

            rows_datas = [
                i for i in zip([y for y in range(len(row_y))], row_y, row_h)
            ]

            # --- Children -----------------------------------------------

            border_tags = [
                i for i in pstyles.TableBorder.sides_xml.values()
            ]

            for element in xml:

                if element.tag == "TableData":

                    if (style := element.get("Style")) is not None:
                        self.style = style

                    if (fill_color := element.get("FillColor")) is not None:
                        self.fill["color"] = fill_color

                    if (fill_shade := element.get("FillShade")) is not None:
                        self.fill["shade"] = dimensions.Dim(
                            float(fill_shade), "pc"
                        )

                    for sub in element:

                        if sub.tag in border_tags:
                            bx = pstyles.TableBorder()

                            if (success := bx.fromxml(sub)):
                                self.borders[bx.side] = bx

                        if sub.tag == "Cell":
                            cx = TableCell(self)

                            if (success := cx.fromxml(sub)):
                                self.cells.append(cx)

            # ------------------------------------------------------------

            self._update_cells_geometry(cols_datas, rows_datas)

            self._update_rowcols_count()

            return True

        return False


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

        #--- Specific attributes to this subclass ------------------------

        self.group_objects = []

        #--- Then, quick setup -------------------------------------------

        PageObject._quick_setup(self, kwargs)

    def fromxml(self, xml):
        succeed = PageObject.fromxml(self, xml)

        if succeed:

            for element in xml:

                if (element_ptype := element.get("PTYPE")) is not None:

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

            return True

        return False


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

        #--- Specific attributes to this subclass ------------------------

        self.pattern = None

        #--- Then, quick setup -------------------------------------------

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

        #--- Specific attributes to this subclass ------------------------

        self.stories = []

        self.columns = {
            "gap": dimensions.Dim(0),
            "count": 0
        }

        self.alignment = None

        #--- Then, quick setup -------------------------------------------

        self._quick_setup(kwargs)

    def _quick_setup(self, settings):
        """
        Method for defining page object settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            PageObject._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                if setting_name == "columns":
                    self.columns["count"] = int(setting_value)

                if setting_name == "columnsgap":
                    self.columns["gap"].value = float(setting_value)

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

    def fromxml(self, xml):
        succeed = PageObject.fromxml(self, xml)

        if succeed:

            # --- Attributes ---------------------------------------------

            if (columns := xml.get("COLUMNS")) is not None:
                self.columns["count"] = int(columns)

            if (columnsgap := xml.get("COLGAPS")) is not None:
                self.columns["gap"].value = float(columnsgap)

            if (alignment := xml.get("ALIGN")) is not None:
                for human, code in xmlc.alignment.items():
                    if alignment == code:
                        self.alignment = human
                        break

            # --- Childs -------------------------------------------------

            for element in xml:

                if element.tag == "PageItemAttributes":

                    for sub in element:

                        if sub.tag == "ItemAttribute":
                            iatt = itemattribute.PageObjectAttribute()

                            if (success := iatt.fromxml(sub)):
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

                    if (success := story.fromxml(element)):
                        if not self.stories:
                            self.have_stories = True

                        self.stories.append(story)

            return True

        return False


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

        #--- Specific attributes to this subclass ------------------------

        self.data = "" # ImageData
        self.data_type = ""
        self.filepath = "" # PFILE

        #--- Then, quick setup -------------------------------------------

        self._quick_setup(kwargs)

    def fromxml(self, xml):
        succeed = PageObject.fromxml(self, xml)

        if succeed:

            # --- Attributes ---------------------------------------------

            ipath = xml.get("PFILE")
            idata_ext = xml.get("inlineImageExt")

            if (idata := xml.get("ImageData")) is not None:
                if idata:
                    self.data = idata

            if (idata_ext := xml.get("inlineImageExt")) is not None:
                if idata_ext:
                    self.data_type = idata_ext

            if (ipath := xml.get("PFILE")) is not None:
                if ipath:
                    self.filepath = ipath

            # ------------------------------------------------------------

            return True

        return False

    def _quick_setup(self, settings):
        """
        Method for defining page object settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            PageObject._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                if setting_name == "filepath":
                    self.filepath = setting_value

                if setting_name == "filedata":
                    self.data = setting_value


class LineObject(PageObject):
    """
    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: SLA DOCUMENT instance
    """

    def __init__(self, sla_parent=False, doc_parent=False, **kwargs):
        PageObject.__init__(self, "line", sla_parent, doc_parent)

        #--- Specific attributes to this subclass ------------------------

        self.line_type = "solid"
        self.line_fill = "Black"
        self.line_stroke = "Black"
        self.line_thickness = dimensions.Dim(1)

        #--- Then, quick setup -------------------------------------------

        PageObject._quick_setup(self, kwargs)

    def fromxml(self, xml):
        succeed = PageObject.fromxml(self, xml)

        if succeed:

            if (line_type := xml.get("PLINEART")) is not None:
                for human, code in PageObject.line_type_xml.items():
                    if line_type == code:
                        self.line_type = human
                        break

            if (fill := xml.get("PCOLOR")) is not None:
                self.line_fill = fill

            if (stroke := xml.get("PCOLOR2")) is not None:
                self.line_stroke = stroke

            if (thickness := xml.get("PWIDTH")) is not None:
                self.line_thickness.value = float(thickness)

            return True

        return False


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

    :ivar pyscribus.pageobjects.RenderBuffer buffer: Content and properties of
        the render frame.
    """

    def __init__(self, sla_parent=False, doc_parent=False):
        PageObject.__init__(self, "render", sla_parent, doc_parent)
        self.buffer = None

    # -----------------------------------------------------------------------

    def fromxml(self, xml):
        succeed = PageObject.fromxml(self, xml)

        if succeed:

            # ------------------------------------------------------------

            for child in xml:

                if child.tag == "LATEX":
                    bfr = RenderBuffer()

                    if (success := bfr.fromxml(child)):
                        self.buffer = bfr

            # ------------------------------------------------------------

            return True

        return False

    def toxml(self):
        xml = PageObject.toxml(self)

        if xml:
            # --- Children -----------------------------------------------

            bfrx = self.buffer.toxml()
            xml.append(bfrx)

            return xml

        return False

    # --- RenderBuffer methods aliases --------------------------------------

    def has_package(self, name):
        """
        Check if package name exists in the LaTeX preamble of the render frame
        buffer.

        :type name: string
        :param name: Name of the package
        :rtype: boolean
        :returns: True if the package exists
        :raise pyscribus.exceptions.UnknownRenderBufferProperty: If the LaTeX 
            preamble property (HeadersRenderProperty) doesn't exists.
        """

        if self.buffer is not None:
            return self.buffer.has_package(name)

    def append_package(self, name, options=""):
        """
        Append a package in the LaTeX preamble of the render frame buffer.

        :type name: str
        :param name: Name of the package
        :type options: str
        :param options: Package's options
        :rtype: boolean
        :returns: True if package appending succeed

        .. note:: As LaTeX additional headers is managed with 
            pageobjects.HeadersRenderProperty, it is better to use this method 
            than editing RenderBuffer.properties.

        Example:

          render_buffer.append_package("csquotes", "strict=true")

          is the equivalent of :

          \\usepackage[strict=true]{csquotes}
        """

        if self.buffer is not None:
            return self.buffer.append_package(name, options)

    def set_fontsize(self, fontsize):
        """
        Set the font size of the render buffer content.

        :type fontsize: float, int
        :param fontsize: Font size in points

        .. note:: As fontsize is a standard render frame property, it is better
            to use this method than editing RenderBuffer.properties.
        """

        if self.buffer is not None:
            return self.buffer.set_fontsize(fontsize)

    # -----------------------------------------------------------------------


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

# Cell object for table =================================================#

class TableCell(xmlc.PyScribusElement):
    """
    Cell in a table object (PAGEOBJECT/TableData/Cell)

    :type pgo_parent: pyscribus.pageobjects.PageObject
    :param pgo_parent: Parent page object instance.
    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    :ivar integer row: Cell row
    :ivar integer column: Cell column
    :ivar string align: Cell vertical alignment

    +---------------+--------------------------------+-----------+
    | Kwargs        | Setting                        | Type      |
    +===============+================================+===========+
    | default       | Equivalent to a fromdefault    | boolean   |
    |               | call, value being True or the  | or string |
    |               | default name                   |           |
    +---------------+--------------------------------+-----------+
    | row           | Row number (ranging from 0)    | integer   |
    +---------------+--------------------------------+-----------+
    | column        | Column number (ranging from 0) | integer   |
    +---------------+--------------------------------+-----------+
    | posx          | X position of the page         | float     |
    +---------------+--------------------------------+-----------+
    | posy          | Y position of the page         | float     |
    +---------------+--------------------------------+-----------+
    | width         | Page width                     | float     |
    +---------------+--------------------------------+-----------+
    | height        | Page height                    | float     |
    +---------------+--------------------------------+-----------+
    | style         | Cell story paragraph style     | string    |
    |               | name                           |           |
    +---------------+--------------------------------+-----------+
    | fillcolor     | Filling color name             | string    |
    +---------------+--------------------------------+-----------+
    | fillshade     | Filling color shade            | float     |
    |               | percentage                     |           |
    +---------------+--------------------------------+-----------+
    | alignment     |                                |           |
    +---------------+--------------------------------+-----------+
    | borders       | Shorthand for rightborder,     | List of   |
    |               | leftborder, topborder,         | floats    |
    |               | bottomborder.                  |           |
    |               |                                |           |
    |               | Read like the CSS margin       |           |
    |               | property:                      |           |
    |               |                                |           |
    |               | **With 1 float in the list :** |           |
    |               |                                |           |
    |               | [top & right & bottom & left]  |           |
    |               |                                |           |
    |               | **With 2 float in the list :** |           |
    |               |                                |           |
    |               | [top & bottom, right & left]   |           |
    |               |                                |           |
    |               | **With 3 float in the list :** |           |
    |               |                                |           |
    |               | [top, right & left, bottom]    |           |
    |               |                                |           |
    |               | **With 4 float in the list :** |           |
    |               |                                |           |
    |               | [top, right, bottom, left]     |           |
    +---------------+--------------------------------+-----------+
    | rightborder   |                                | float     |
    +---------------+--------------------------------+-----------+
    | leftborder    |                                | float     |
    +---------------+--------------------------------+-----------+
    | topborder     |                                | float     |
    +---------------+--------------------------------+-----------+
    | bottomborder  |                                | float     |
    +---------------+--------------------------------+-----------+
    | padding       | Shorthand for rightpadding,    | List of   |
    |               | leftpadding, toppadding,       | floats    |
    |               | bottompadding.                 |           |
    |               |                                |           |
    |               | Read like the CSS margin       |           |
    |               | property:                      |           |
    |               |                                |           |
    |               | **With 1 float in the list :** |           |
    |               |                                |           |
    |               | [top & right & bottom & left]  |           |
    |               |                                |           |
    |               | **With 2 float in the list :** |           |
    |               |                                |           |
    |               | [top & bottom, right & left]   |           |
    |               |                                |           |
    |               | **With 3 float in the list :** |           |
    |               |                                |           |
    |               | [top, right & left, bottom]    |           |
    |               |                                |           |
    |               | **With 4 float in the list :** |           |
    |               |                                |           |
    |               | [top, right, bottom, left]     |           |
    +---------------+--------------------------------+-----------+
    | rightpadding  |                                | float     |
    +---------------+--------------------------------+-----------+
    | leftpadding   |                                | float     |
    +---------------+--------------------------------+-----------+
    | toppadding    |                                | float     |
    +---------------+--------------------------------+-----------+
    | bottompadding |                                | float     |
    +---------------+--------------------------------+-----------+
    """

    # TextColumns="1" 
    # TextColGap="0" 
    # TextDistLeft="0" TextDistTop="0" TextDistBottom="0" TextDistRight="0" 
    # Flop="0" 

    vertical_align = {"top": "0", "center": "1", "bottom": "2"}

    def __init__(self, pgo_parent=False, **kwargs):
        super().__init__()

        self.pgo_parent = pgo_parent

        # Row, column, box -----------------------------------------------

        self.row = None
        self.column = None
        self.box = dimensions.DimBox()

        # Appearance of the cell -----------------------------------------

        self.style = None

        self.fill = {"color": "None", "shade": None}

        self.borders = {
            "left": None, "right": None,
            "top": None, "bottom": None
        }

        self.padding = {
            "left": None, "right": None,
            "top": None, "bottom": None
        }

        self.align = None

        # Content of the cell --------------------------------------------

        self.story = None

        # --- Quick setup --------------------------------------------

        if kwargs:
            self._quick_setup(kwargs)

    def fromdefault(self):

        if self.pgo_parent:
            self.story = stories.Story(
                self.pgo_parent.sla_parent,
                self.pgo_parent.doc_parent,
                self
            )
        else:
            self.story = stories.Story()

        self.story.fromdefault()

        self.padding = {
            "left": dimensions.Dim(1),
            "right": dimensions.Dim(1),
            "top": dimensions.Dim(1),
            "bottom": dimensions.Dim(1)
        }

        self.align = "top"

    def _quick_setup(self, settings):
        """
        Method for defining table cell settings from class instanciation
        kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        def shortcut_geometry_setting(objattribute, setting_value):
            """
            Solve a setting value like the CSS margin property.

            - If only one value : same border/padding for all sides
            - If two values: vertical and horizontal borders/padding
            - If three values: top horizontal bottom
            - If four values: top right bottom left

            :type objattribute: dict
            :param objattribute: instance attribute to modify
            :type setting_value: list
            :param setting_value: setting value
            :rtype: dict
            :returns: modified instance attribute
            """

            if isinstance(setting_value, list):
                setting_len = len(setting_value)

                if setting_len == 1:

                    for side in ["top", "right", "bottom", "left"]:
                        objattribute[side].value = float(
                            setting_value[0]
                        )

                if setting_len == 2:
                    sides = zip(
                        [["top", "bottom"], ["right", "left"]],
                        setting_value
                    )

                    for side in sides:
                        for s in side[0]:
                            objattribute[s].value = float(side[1])

                if setting_len == 3:
                    objattribute["top"].value = float(setting_value[0])

                    for side in ["right", "left"]:
                        objattribute[side].value = float(
                            setting_value[1]
                        )

                    objattribute["bottom"].value = float(
                        setting_value[2]
                    )

                if setting_len == 4:
                    sides = zip(
                        ["top", "right", "bottom", "left"],
                        setting_value
                    )

                    for side in sides:
                        objattribute[side[0]].value = float(side[1])

            return objattribute

        if settings:
            xmlc.PyScribusElement._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                # Cell style --------------------------------------------------

                if setting_name == "fillcolor":
                    self.fill["color"] = setting_value

                if setting_name == "fillshade":
                    self.fill["shade"] = dimensions.Dim(
                        float(setting_value), "pc"
                    )

                if setting_name == "style":
                    self.style = setting_value

                if setting_name == "alignment":

                    if setting_value in TableCell.vertical_align.keys():
                        self.align = setting_value
                    else:
                        self.align = "top"

                # Borders -----------------------------------------------------

                if setting_name in [
                        "rightborder", "leftborder",
                        "topborder", "bottomborder"]:
                    side = setting_name.split("border")[0]
                    self.borders[side].value = float(setting_value)

                if setting_name == "borders":
                    self.borders = shortcut_geometry_setting(
                        self.borders, setting_value
                    )

                # Padding -----------------------------------------------------

                if setting_name in [
                        "rightpadding", "leftpadding",
                        "toppadding", "bottompadding"]:
                    side = setting_name.split("padding")[0]
                    self.padding[side].value = float(setting_value)

                if setting_name == "padding":
                    self.padding = shortcut_geometry_setting(
                        self.padding, setting_value
                    )

                # Cell position -----------------------------------------------

                if setting_name == "row":
                    self.row = setting_value

                if setting_name == "column":
                    self.column = setting_value

                # Cell box ----------------------------------------------------

                if setting_name == "posx":
                    self.box.setx("top-left", float(setting_value))

                if setting_name == "posy":
                    self.box.sety("top-left", float(setting_value))

                if setting_name == "width":
                    self.box.dims["width"].value = float(setting_value)

                if setting_name == "height":
                    self.box.dims["height"].value = float(setting_value)

    def fromxml(self, xml):
        """
        Parses XML of a SLA table cell.

        :type xml: lxml._Element
        :param xml: SLA table cell as lxml._Element

        :rtype: bool
        :returns: bool
        """

        if xml.tag == "Cell":
            border_tags = [
                i for i in pstyles.TableBorder.sides_xml.values()
            ]

            # Position of the cell -----------------------------------

            row = xml.get("Row")
            column = xml.get("Column")

            if row is None or column is None:
                raise exceptions.InsaneSLAValue(
                    "A table cell has no @Row or @Column attribute."
                )
            else:
                self.row = int(row)
                self.column = int(column)

            # Cell attributes ----------------------------------------

            if (style := xml.get("Style")) is not None:
                self.style = style

            if (align := xml.get("TextVertAlign")) is not None:

                for human,code in TableCell.vertical_align.items():
                    if align == code:
                        self.align = human
                        break

            if (fill_color := xml.get("FillColor")) is not None:
                self.fill["color"] = fill_color

            if (fill_shade := xml.get("FillShade")) is not None:
                self.fill["shade"] = dimensions.Dim(
                    float(fill_shade), "pc"
                )

            for side in ["left", "right", "top", "bottom"]:
                att_name = "{}Padding".format(side.capitalize())

                if (att := xml.get(att_name)) is not None:
                    self.padding[side] = dimensions.Dim(float(att))

            for element in xml:

                # Story of the cell --------------------------------------

                if element.tag == "StoryText":

                    if self.pgo_parent:
                        story = stories.Story(
                            self.pgo_parent.sla_parent,
                            self.pgo_parent.doc_parent,
                            self
                        )
                    else:
                        story = stories.Story(pgo_parent=self)

                    success = story.fromxml(element)

                    if success:
                        self.story = story

                # Borders of the cell if they are different of the table -
                # borders.

                if element.tag in border_tags:
                    bx = pstyles.TableBorder()
                    success = bx.fromxml(element)

                    if success:
                        self.borders[bx.side] = bx

            return True

        return False

    def toxml(self):
        """
        Return the cell as XML element.

        :rtype: lxml._Element
        """

        xml = ET.Element("Cell")

        # Attributes ---------------------------------------------

        xml.attrib["Row"] = str(self.row)
        xml.attrib["Column"] = str(self.column)

        xml.attrib["FillColor"] = self.fill["color"]

        if self.style is None:
            xml.attrib["Style"] = ""
        else:
            xml.attrib["Style"] = self.style

        if self.align is None:
            xml.attrib["TextVertAlign"] = TableCell.vertical_align["top"]
        else:
            xml.attrib["TextVertAlign"] = TableCell.vertical_align[self.align]

        if self.fill["shade"] is None:
            xml.attrib["FillShade"] = "100"
        else:
            xml.attrib["FillShade"] = self.fill["shade"].toxmlstr(True)

        for side in ["left", "right", "top", "bottom"]:
            att_name = "{}Padding".format(side.capitalize())

            if self.padding[side] is not None:
                xml.attrib[att_name] = self.padding[side].toxmlstr(True)

        # Cell borders -------------------------------------------

        for side in ["left", "right", "top", "bottom"]:
            if self.borders[side] is not None:
                bx = self.borders[side].toxml()
                xml.append(bx)

        # Story of the cell --------------------------------------

        if self.story is None:
            story = stories.Story()
            story.fromdefault()

        sx = self.story.toxml()
        xml.append(sx)

        # --------------------------------------------------------

        return xml

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

        .. note:: As LaTeX additional headers is managed with 
            pageobjects.HeadersRenderProperty, it is better to use this method 
            than editing RenderBuffer.properties.

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

            if (dpi := xml.get("DPI")) is not None:
                self.dpi.value = float(dpi)

            if (use_preamble := xml.get("USE_PREAMBLE")) is not None:
                self.use_preamble = xmlc.num_to_bool(use_preamble)

            if (configfile := xml.get("ConfigFile")) is not None:
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
            if (name := xml.get("name")) is not None:
                self.name = name

            if (value := xml.get("value")) is not None:
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
            wx,wy = xml.get("WX"),xml.get("WY")

            if (target := xml.get("Target")) is not None:
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
