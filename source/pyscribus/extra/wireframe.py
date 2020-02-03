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
Reads SLA file and use Pillow to draw a schematic picture of all page
and page objects.
"""

# Imports ===============================================================#

import math

from PIL import Image, ImageDraw

import pyscribus.dimensions as dimensions
import pyscribus.pageobjects as pageobjects
import pyscribus.pages as pages

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class WireframeObject:
    """
    Wireframe object : something to draw on the wireframe, like pages,
    page objects.

    :type sla_object: pyscribus.pages.Page, pyscribus.pageobjects.PageObject
    :param sla_object: PyScribus instance of drawnable object
    """

    def __init__(self, sla_object=False):
        self.box = False
        self.bleed = False

        self.is_page = False
        self.type = "undefined"
        self.group_objects = []

        # Pages have layer -1, as 0 is the lower layer available
        self.layer = -1

        self.draw_settings = {
            "fill": "",
            "outline": "",
            "bleed": "red"
        }

        if sla_object:
            self.from_object(sla_object)

    def from_object(self, sla_object):

        if isinstance(sla_object, pages.Page):
            self.is_page = True
            self.type = "page"
        else:
            self.is_page = False
            type_ok = False

            for class_test in [
                    pageobjects.LatexObject,
                    pageobjects.RenderObject]:

                if isinstance(sla_object, class_test):
                    self.type = "render"
                    type_ok = True
                    break

            if not type_ok:

                for human, class_test in pageobjects.po_type_classes.items():

                    if isinstance(sla_object, class_test):
                        self.type = human
                        type_ok = True
                        break

        if self.type == "group":
            self.group_objects = sla_object.group_objects

        if isinstance(sla_object, pageobjects.PageObject):

            if sla_object.rotated:
                self.box = sla_object.rotated_box
            else:
                self.box = sla_object.box

            self.layer = sla_object.layer

        else:
            self.box = sla_object.box

    def draw_on_canvas(self, canvas, bleed=False):

        if bleed and self.bleed:
            tx = self.box.coords["top-left"][0].value - self.bleed["left"]
            ty = self.box.coords["top-left"][1].value - self.bleed["top"]
            bx = self.box.coords["bottom-right"][0].value + self.bleed["right"]
            by = self.box.coords["bottom-right"][1].value + self.bleed["bottom"]

            bleed_rect = ((tx, ty), (bx, by))
            canvas.rectangle(bleed_rect, outline="red")

        rect = (
            (
                self.box.coords["top-left"][0],
                self.box.coords["top-left"][1]
            ),
            (
                self.box.coords["bottom-right"][0],
                self.box.coords["bottom-right"][1]
            ),
        )

        if self.draw_settings["fill"] and self.draw_settings["outline"]:

            canvas.rectangle(
                rect,
                fill=self.draw_settings["fill"],
                outline=self.draw_settings["outline"]
            )

        else:

            if self.draw_settings["fill"]:
                canvas.rectangle(rect, fill=self.draw_settings["fill"])

            if self.draw_settings["outline"]:
                canvas.rectangle(rect, outline=self.draw_settings["outline"])

        if self.type == "group":

            for subpo in self.group_objects:
                s = WireframeObject(subpo)
                s.draw_on_canvas(canvas, bleed)

        return canvas


class Wireframe:
    """
    Wireframe canvas.

    Reads SLA file and use Pillow to draw a schematic picture of all page
    and page objects.

    :ivar list pages: List of pages as WireframeObject
    :ivar list page_objects: List of page objects as WireframeObject
    """

    stylesheet = {
        "page": {"fill": "white", "outline": ""},
        "text": {"fill": "lightgrey", "outline": "black"},
        "line": {"fill": "", "outline": "black"},
        "image": {"fill": "lightblue", "outline": "blue"},
        "table": {"fill": "", "outline": "darkgreen"},
        "render": {"fill": "lightgreen", "outline": "black"},
        "polygon": {"fill": "yellow", "outline": "black"},
    }

    def __init__(self):
        self.pages = []
        self.page_objects = []

        self.bleed = {
            "top": dimensions.Dim(0), "right": dimensions.Dim(0),
            "left": dimensions.Dim(0), "bottom": dimensions.Dim(0)
        }

    def from_sla(self, sla):
        """
        Load all drawnable objects of sla file.

        :type sla: string
        :param sla: SLA file path
        """
        self.bleed = sla.documents[0].bleed

        for page in sla.documents[0].pages:
            wo = WireframeObject(page)
            wo.bleed = self.bleed
            self.pages.append(wo)

        for pago in sla.documents[0].page_objects:
            wo = WireframeObject(pago)
            self.page_objects.append(wo)

    def append(self, sla_object):

        def add(obj, sla_obj):
            if sla_obj.is_page:
                obj.pages.append(sla_obj)
            else:
                obj.page_objects.append(sla_obj)

            return obj

        if isinstance(sla_object, WireframeObject):
            self = add(self, sla_object)
        else:
            self = add(self, WireframeObject(sla_object))

    def _image_size(self, margins=[0,0]):
        max_x = float()
        max_y = float()

        for po in self.page_objects:
            trx = po.box.coords["top-right"][0].value
            bry = po.box.coords["bottom-right"][1].value

            if trx > max_x:
                max_x = trx

            if bry > max_y:
                max_y = bry

        # We add a little margin

        max_x += margins[0]
        max_y += margins[1]

        return (int(max_x), int(max_y))

    def draw(self, **kwargs):
        """
        Returns Pillow Image instance or bool if [output] option is set.

        :type kwargs: dict
        :param kwargs: Draw options

        **Draw options :**

        +------------------+---------------------------------------+---------------------------+---------+
        | kwargs key       | Use                                   | Type                      | Default |
        +==================+=======================================+===========================+=========+
        | default_outline  | Outline color used if an object has   | boolean or Pillow color   | "black" |
        |                  | no fill and no outline color          |                           |         |
        |                  | defined.                              |                           |         |
        +------------------+---------------------------------------+---------------------------+---------+
        | pages            | Draw all page or only pages in a      | "all" or                  | "all"   |
        |                  | list of page numbers.                 | list of integers [1,...]  |         |
        +------------------+---------------------------------------+---------------------------+---------+
        | layers           | Draw all layers or only layers in     | "all" or                  | "all"   |
        |                  | a list of layer numbers.              | list of integers [1,...]  |         |
        +------------------+---------------------------------------+---------------------------+---------+
        | background_color | Background color of the image         | Pillow color              | "grey"  |
        +------------------+---------------------------------------+---------------------------+---------+
        | output           | File path of the output file          | str                       | False   |
        +------------------+---------------------------------------+---------------------------+---------+
        | stylesheet       | Fill and outline setting according to | boolean or dict           | False   |
        |                  | the type of object to draw.           |                           |         |
        |                  |                                       | (as Wireframe.stylesheet) |         |
        |                  | True for default stylesheet.          |                           |         |
        +------------------+---------------------------------------+---------------------------+---------+
        | landmark         | Draw landmark lines at 0,0.           | boolean                   | True    |
        +------------------+---------------------------------------+---------------------------+---------+
        | bleed            | Draw page bleeds                      | boolean                   | True    |
        +------------------+---------------------------------------+---------------------------+---------+
        """

        draw_pages = "all"
        draw_layers = "all"
        draw_landmark = True
        draw_bleed = True

        out_file = False

        canvas_margins = [0,0]
        background_color = "grey"

        default_outline = "black"

        use_stylesheet = False
        stylesheet = Wireframe.stylesheet

        # --- Options processing ------------------------------------

        for opt_name,opt_value in kwargs.items():

            if opt_name == "layers":
                draw_layers = opt_value

            if opt_name == "pages":

                if isinstance(opt_value, bool):
                    if opt_value:
                        draw_pages = "all"
                    else:
                        draw_pages = "none"
                else:
                    draw_pages = opt_value

            if opt_name == "margins":
                canvas_margins = opt_value

            if opt_name == "background":
                background_color = opt_value

            if opt_name == "default_outline":
                default_outline = opt_value

            if opt_name == "landmark":
                if opt_value:
                    draw_landmark = True
                else:
                    draw_landmark = False

            if opt_name == "bleed":
                if opt_value:
                    draw_bleed = True
                else:
                    draw_bleed = False

            if opt_name == "stylesheet":

                if isinstance(opt_value, bool):
                    if opt_value:
                        use_stylesheet = True
                else:
                    stylesheet = opt_value
                    use_stylesheet = True

            if opt_name == "output":
                out_file = opt_value

        # --- Image creation ----------------------------------------

        image_size = self._image_size(canvas_margins)

        image = Image.new("RGB", image_size, color=background_color)
        canvas = ImageDraw.Draw(image)

        # --- Drawing landmark --------------------------------------

        if draw_landmark:
            canvas.line(((-5,0),(5,0)), fill="red")
            canvas.line(((0,-5),(0,-5)), fill="red")

        # --- Using default_outline or stylesheet -------------------

        if use_stylesheet:
            # --- Using stylesheet ----------------------------------

            for object_set in [self.pages, self.page_objects]:

                for obj in object_set:
                    key = False

                    if obj.type in stylesheet:
                        key = obj.type

                    if key:
                        obj.draw_settings["fill"] = stylesheet[key]["fill"]
                        obj.draw_settings["outline"] = stylesheet[key]["outline"]

        else:
            # --- Using default_outline if no defined outline -------

            if default_outline:

                for object_set in [self.pages, self.page_objects]:

                    for obj in object_set:
                        drawed = False

                        if obj.draw_settings["fill"] or obj.draw_settings["outline"]:
                            drawed = True

                        if not drawed:
                            obj.draw_settings["outline"] = default_outline

            # -------------------------------------------------------

        # --- Drawing page and page objects -------------------------

        if draw_pages != "none":

            if draw_pages == "all":

                for page in self.pages:
                    canvas = page.draw_on_canvas(canvas, draw_bleed)

            else:
                # Only pages in draw_pages list

                for page in self.pages:

                    if page.number in draw_pages:
                        canvas = page.draw_on_canvas(canvas, draw_bleed)

        if draw_layers == "all":

            for pago in self.page_objects:
                canvas = pago.draw_on_canvas(canvas)

        else:
            # Only page objects in draw_layers list layers

            for pago in self.page_objects:

                if pago.layer in draw_layers:
                    canvas = pago.draw_on_canvas(canvas)

        # -----------------------------------------------------------

        if out_file:
            image.save(out_file)

            return True
        else:
            return image

# vim:set shiftwidth=4 softtabstop=4 spl=en:
