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
PyScribus classes for measures and geometrical manipulations.
"""

import copy
import math

from pyscribus.common.math import PICA_TO_MM,INCH_TO_MM

import pyscribus.exceptions as exceptions

import pyscribus.papers.ansi as ansipaper
import pyscribus.papers.iso216 as iso216paper

from pyscribus.common.xml import *

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class Dim:
    """
    Dimension object. Allows to convert and export in the correct unit.

    :type value: float,int
    :param value: Value of the dimension
    :type unit: str
    :param unit: Unit of the dimension.
    :type is_int: boolean
    :param is_int: Use integer instead of float type for value

    :ivar float,int value: Value of the dimension in the original unit
    :ivar string unit: Unit of the dimension

    +-------------------------+---------------+
    | Unit / Notation         | unit argument |
    +=========================+===============+
    | Milimeter               | mm            |
    +-------------------------+---------------+
    | Pica point              | pica, pt      |
    +-------------------------+---------------+
    | Percentage (0 to 100)   | perc, pc      |
    +-------------------------+---------------+
    | Percentage (0.0 to 1)   | pcdecim       |
    +-------------------------+---------------+
    | Calligraphic pen degree | cdeg          |
    +-------------------------+---------------+
    | Regular degree          | deg           |
    +-------------------------+---------------+
    | Dot per inch (DPI/PPP)  | dpi, ppp, ppi |
    +-------------------------+---------------+
    | Line per inch (LPI)     | lpi           |
    +-------------------------+---------------+
    """

    # 1 pica point = 25,4/72 milimeters
    PICA_TO_MM = (25.4 / 72)

    UNIT_ARGS = {
        "mm": ["mm"],
        "pica": ["pica", "pt"],
        "perc": ["perc", "pc"],
        "pcdecim": ["pcdecim"],
        "cdeg": ["cdeg"],
        "deg": ["deg"],
        "dpi": ["dpi", "ppp", "ppi"],
        "lpi": ["lpi"],
    }

    def __init__(self, value, unit="pica", is_int=False, original_unit=False):
        self.is_int = False

        if is_int:
            self.is_int = True
            value = int(value)

        self.value = value

        self.set_unit(unit)

        if original_unit:
            self.from_original_unit(original_unit)

        self.check_value()

    #--- Checking, setting the unit --------------------------------------

    def from_original_unit(self, original_unit):
        pass

    def check_value(self):
        """
        Check value validity according to unit.

        :rtype: boolean
        :return: True if the value is valid
        :raises pyscribus.exceptions.InvalidDim: Raised if value is invalid.
        """

        if self.unit in ["pica", "pt"]:

            if self.value < 0:
                raise exceptions.InvalidDim(
                    "Pica points must not be inferior to 0."
                )

        if self.unit == "dpi":

            if self.value < 0:
                raise exceptions.InvalidDim(
                    "DPI/PPP must be a positive number"
                )

        if self.unit == "lpi":

            if self.value < 0:
                raise exceptions.InvalidDim(
                    "LPI must be a positive number"
                )

        if self.unit == "cdeg":

            if self.value >= 0:
                if self.value <= 180:
                    return True
                else:
                    raise exceptions.InvalidDim(
                        "Calligraph pen angle must range from 0 to 180"
                    )
            else:
                raise exceptions.InvalidDim(
                    "Calligraph pen angle must range from 0 to 180"
                )

        if self.unit == "deg":

            if self.value >= 0:

                if self.value <= 360:
                    return True
                else:
                    raise exceptions.InvalidDim(
                        "Angle must range from 0 to 360"
                    )

            else:
                raise exceptions.InvalidDim(
                    "Angle must range from 0 to 360"
                )

        return True

    def set_unit(self, unit="pica"):
        """
        Set the unit used.

        :type value: float,int
        :param value: Value of the dimension
        :type unit: str
        :param unit: Unit of the dimension.
        :rtype: boolean
        :return: True if the unit is valid

        +-------------------------+---------------+
        | Unit / Notation         | unit argument |
        +=========================+===============+
        | Milimeter               | mm            |
        +-------------------------+---------------+
        | Pica point              | pica, pt      |
        +-------------------------+---------------+
        | Percentage (0 to 100)   | perc, pc      |
        +-------------------------+---------------+
        | Percentage (0.0 to 1)   | pcdecim       |
        +-------------------------+---------------+
        | Calligraphic pen degree | cdeg          |
        +-------------------------+---------------+
        | Regular degree          | deg           |
        +-------------------------+---------------+
        | Dot per inch (DPI/PPP)  | dpi, ppp, ppi |
        +-------------------------+---------------+
        | Line per inch (LPI)     | lpi           |
        +-------------------------+---------------+
        """

        tmp_unit = unit.lower()
        valid_unit = False

        for code,args in Dim.UNIT_ARGS.items():

            if tmp_unit in args:
                self.unit = code
                valid_unit = True
                break

        return valid_unit

    #--- XML export ------------------------------------------------------

    def toxmlstr(self, no_useless_decimals=False):
        """
        Returns a XML string of the dimension according to its unit.

        :type no_useless_decimals: boolean
        :param no_useless_decimals: Returns integer instead of float if
            decimals are 0. So 1.0 -> 1 ; 1.1 -> 1.1.
        :rtype: str
        :return: str
        """

        def decimals(n):
            if float(n) == int(n):
                return int(n)
            else:
                return n

        if self.unit not in ["perc", "pcdecim", "cdeg", "deg", "lpi", "dpi"]:
            if no_useless_decimals:
                pica = self.topica()
                return str(decimals(pica))
            else:
                return str(self.topica())
        else:
            if self.unit == "pcdecim":
                if self.value == 1.0:
                    return "1"
                else:
                    if no_useless_decimals:
                        return str(decimals(self.value))
                    else:
                        return str(self.value)
            else:
                if no_useless_decimals:
                    return str(decimals(self.value))
                else:
                    return str(self.value)

    def toxml(self):
        """
        Alias of Dimension.toxmlstr()

        Returns a XML string of the dimension according to its unit.

        :rtype: str
        :return: str
        """

        return self.toxmlstr()

    #--- Conversion into other units -------------------------------------

    def _ceil(self, value, ceil=False):
        """
        Ceil value if ceil is True.

        :type value: float,int
        :param value: Value to ceil (or not)
        :type ceil: boolean
        :param ceil: If True, apply ceil to value
        :rtype: float,int
        :return: Ceiled (or not) number
        """

        if ceil:
            return math.ceil(value)
        else:
            return value

    def _convertorval(self, obj, value, unit):
        """
        Returns a Dim object with unit <unit> if <obj>, or <value>.

        :rtype: float,int,Dim
        :return: Dim object or Dim value
        """

        if obj:
            return Dim(value, unit)
        else:
            return value

    def is_convertable_length(self):
        """
        :rtype: boolean
        :return: If the Dim instance is a convertable length
        """

        if self.unit in ["perc", "pcdecim", "cdeg", "deg", "dpi", "lpi"]:
            return False

        return True

    def topica(self, ceil=False, obj=False):
        """
        Returns the value of Dim in pica point unit.
        Raise ValueError if Dim is not convertable

        :type ceil: boolean
        :param ceil: If True, apply ceil to returned value
        :type obj: boolean
        :param obj: If True, returns a Dim object instead of value.
        """

        if not self.is_convertable_length():
            raise exceptions.IncompatibleDim(
                "Can't convert that ({}) into pica points".format(self.unit)
            )

        if self.unit == "pica":
            return self._convertorval(
                obj, self._ceil(self.value, ceil), "pica"
            )

        if self.unit == "mm":
            return self._convertorval(
                obj, self._ceil(self.value / Dim.PICA_TO_MM, ceil), "pica"
            )

    def todpi(self, ceil=False, obj=False):
        """
        Returns the value of Dim in DPI unit.
        Raise ValueError if Dim is not convertable

        :type ceil: boolean
        :param ceil: If True, apply ceil to returned value
        :type obj: boolean
        :param obj: If True, returns a Dim object instead of value.
        """

        if self.unit == "lpi":
            return self._convertorval(
                obj, self._ceil(self.value * 16), "dpi"
            )
        else:
            raise exceptions.IncompatibleDim(
                "Can't convert that into DPI"
            )

    def topc(self, ceil, obj=False):
        """
        Returns the value of Dim as integer percentage.
        Raise ValueError if Dim is not convertable

        :type ceil: boolean
        :param ceil: If True, apply ceil to returned value
        :type obj: boolean
        :param obj: If True, returns a Dim object instead of value.
        """

        if self.unit == "pcdecim":
            return self._convertorval(
                obj, self._ceil(self.value * 100), "pc"
            )
        else:
            raise exceptions.IncompatibleDim(
                "Can't convert that into percentage"
            )

    def tolpi(self, ceil=False, obj=False):
        """
        Returns the value of Dim in LPI unit.
        Raise ValueError if Dim is not convertable

        :type ceil: boolean
        :param ceil: If True, apply ceil to returned value
        :type obj: boolean
        :param obj: If True, returns a Dim object instead of value.
        """

        if self.unit == "dpi":
            return self._convertorval(
                obj, self._ceil(self.value / 16), "lpi"
            )
        else:
            raise exceptions.IncompatibleDim(
                "Can't convert that into LPI"
            )

    def tomm(self, ceil=False, obj=False):
        """
        Returns the value of Dim in milimeter unit.

        :type ceil: boolean
        :param ceil: If True, apply ceil to returned value
        :type obj: boolean
        :param obj: If True, returns a Dim object instead of value.
        """

        if not self.is_convertable_length():
            raise exceptions.IncompatibleDim(
                "Can't convert that into milimeters"
            )

        if self.unit == "pica":
            return self._convertorval(
                obj, self._ceil(self.value * Dim.PICA_TO_MM, ceil), "mm"
            )

        if self.unit == "mm":
            return self._convertorval(
                obj, self._ceil(self.value, ceil), "mm"
            )

    #--- Defaults --------------------------------------------------------

    def fromdefault(self, default):
        """
        Set Dim attributes according to a named default.

        :type default: str
        :param default: Name of the set of defaults.
        :rtype: boolean
        :return: boolean
        """

        if default.startswith("a4-"):
            self.set_unit("pica")

            if default == "a4-width":
                self.value = iso216paper.A4.WIDTH

            if default == "a4-height":
                self.value = iso216paper.A4.HEIGHT

        if default.startswith("letter-"):
            self.set_unit("pica")

            if default == "letter-width":
                self.value = ansipaper.Letter.WIDTH

            if default == "letter-height":
                self.value = ansipaper.Letter.HEIGHT

        return True

    #--- Python __ methods -----------------------------------------------

    def __bool__(self):
        return bool(self.value)

    def __str__(self):
        r,u = str(self.value),""

        if self.unit in Dim.UNIT_ARGS.keys():
            short = {"mm": "mm", "perc": "%", "pica": "pt", "lpi": "lpi"}

            if self.unit in short:
                u = short[self.unit]

            if self.unit in ["cdeg", "deg"]:
                u = "°"

        else:
            raise exceptions.UnknownDimUnit(self.unit)

        return "{} {}".format(r, u)

    def __repr__(self):
        return "Dim(value={}, unit={}, is_int={})".format(
            self.value, self.unit, self.is_int
        )

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __iadd__(self, dim):

        if isinstance(dim, float):
            self.value += dim

        if isinstance(dim, Dim):
            if dim.unit == self.unit:
                self.value += dim.value
            else:
                raise exceptions.IncompatibleDim()

        return self

    def __isub__(self, dim):

        if isinstance(dim, float):
            self.value -= dim

        if isinstance(dim, Dim):
            if dim.unit == self.unit:
                self.value -= dim.value
            else:
                raise exceptions.IncompatibleDim()

        return self

    def __imul__(self, dim):

        if isinstance(dim, float):
            self.value *= dim

        if isinstance(dim, Dim):
            if dim.unit == self.unit:
                self.value *= dim.value
            else:
                raise exceptions.IncompatibleDim()

    def __sub__(self, dim):
        return self.__isub__(dim)

    def __add__(self, dim):
        return self.__iadd__(dim)

    def __mul__(self, dim):
        return self.__imul__(dim)


class DimBox:
    """
    Box/rectangle object to manipulate Scribus frames coordinates.

    :type kwargs: dict
    :param kwargs: kwargs (see kwargs table)

    :ivar dict dims: Width and height of the box as Dim objects
    :ivar dict coords: Coordinates of the box, dict of list of
        Dim objects ([x, y]) for each point
    :ivar Dim rotation: Rotation angle of the box as Dim object
        (unit : degree)
    :ivar dict rotated_coords: Coordinates of the box when rotated by
        rotation degree

    +-------------------------+------------+
    | Box point coordinate    | kwargs key |
    +=========================+============+
    | Top left x position     | top_lx     |
    +-------------------------+------------+
    | Top left y position     | top_ly     |
    +-------------------------+------------+
    | Top right x position    | top_rx     |
    +-------------------------+------------+
    | Top right y position    | top_ry     |
    +-------------------------+------------+
    | Bottom right x position | bottom_rx  |
    +-------------------------+------------+
    | Bottom right y position | bottom_ry  |
    +-------------------------+------------+
    | Box width               | width      |
    +-------------------------+------------+
    | Box height              | height     |
    +-------------------------+------------+
    """

    def __init__(self,**kwargs):
        # X,Y coordinates for each corner
        # Use setx, sety, getx, gety methods as shorthands
        self.coords = {
            "top-left": [Dim(0), Dim(0)],
            "top-right": [Dim(0), Dim(0)],
            "bottom-left": [Dim(0), Dim(0)],
            "bottom-right": [Dim(0), Dim(0)],
        }

        # Height and width
        self.dims = {"width": Dim(0), "height": Dim(0)}

        # Coords & angle for rotated boxes --------------------------
        # NOTE rotated_coords is modified through set_box and rotate

        self.rotation = Dim(0, "deg")
        self.rotated_coords = {
            "top-left": [Dim(0), Dim(0)],
            "top-right": [Dim(0), Dim(0)],
            "bottom-left": [Dim(0), Dim(0)],
            "bottom-right": [Dim(0), Dim(0)],
        }

        # -----------------------------------------------------------

        self.set_box(kwargs=kwargs)

    #--- Shorthands for corners coordinates ------------------------------

    def _setxy(self, corner, value, xy, rotated=False):
        if corner.lower() in [
                "top-left", "top-right",
                "bottom-left", "bottom-right"]:

            if xy == "x":
                if rotated:
                    self.rotated_coords[corner][0].value = value
                else:
                    self.coords[corner][0].value = value
            else:
                if rotated:
                    self.rotated_coords[corner][1].value = value
                else:
                    self.coords[corner][1].value = value

            return True
        else:
            raise KeyError()

    def _getxy(self, corner, xy, rotated=False):
        if corner.lower() in [
                "top-left", "top-right",
                "bottom-left", "bottom-right"]:
            if xy == "x":
                if rotated:
                    return self.rotated_coords[corner][0].value
                else:
                    return self.coords[corner][0].value
            else:
                if rotated:
                    return self.rotated_coords[corner][1].value
                else:
                    return self.coords[corner][1].value
        else:
            raise KeyError()

    def setx(self, corner, value, rotated=False):
        return self._setxy(corner, value, "x", rotated)

    def sety(self, corner, value, rotated=False):
        return self._setxy(corner, value, "y", rotated)

    def getx(self, corner, rotated=False):
        return self._getxy(corner, "x", rotated)

    def gety(self, corner, rotated=False):
        return self._getxy(corner, "y", rotated)

    #--- Box modification ------------------------------------------------

    def move(self, posx=0, posy=0, refpoint="top-left"):
        """
        Move the box at posx, posy position.

        :type posx: float
        :param posx: New X position
        :type posy: float
        :param posy: New Y position
        :type refpoint: string
        :param refpoint: Coordinate point of reference (DimBox.coords key)
        :rtype: boolean
        """

        origin_x,origin_y = None,None

        if refpoint in self.coords.keys():
            origin_x = self.coords[refpoint][0].value
            origin_y = self.coords[refpoint][1].value

        if origin_x is not None and origin_y is not None:

            if origin_x != posx or origin_y != posy:
                # Noving the box according to the reference point

                if refpoint == "top-left":
                    self.set_box(
                        top_lx=posx, top_ly=posy,
                        width=self.dims["width"].value,
                        height=self.dims["height"].value,
                    )

                    return True

            else:
                # Moving the box at the exact same position is not a mistake
                # even if it's useless
                return True

        return False

    def translate(self, amountx=0, amounty=0, refpoint="top-left"):
        """
        Move the box by an amount of amountx, amounty

        :type amountx: float
        :param amountx: Amount of X translation
        :type amounty: float
        :param amounty: Amount of Y translation
        :type refpoint: string
        :param refpoint: Coordinate point of reference (DimBox.coords key)
        :rtype: boolean
        """

        origin_x,origin_y = None,None

        if refpoint in self.coords.keys():
            origin_x = self.coords[refpoint][0].value
            origin_y = self.coords[refpoint][1].value

        if origin_x is not None and origin_y is not None:

            # Translating the box by amountx, amounty

            if refpoint == "topleft":
                npx = self.coords["top-left"][0].value + amountx
                npy = self.coords["top-left"][1].value + amounty

                self.set_box(
                    top_lx=npx, top_ly=npy,
                    width=self.dims["width"].value,
                    height=self.dims["height"].value,
                )

                return True

        return False

    def set_box(self, **kwargs):
        """
        Set all coordinates of the box from a set a coordinates
        and/or width & height.

        +-------------------------+------------+
        | Box point coordinate    | kwargs key |
        +=========================+============+
        | Top left x position     | top_lx     |
        +-------------------------+------------+
        | Top left y position     | top_ly     |
        +-------------------------+------------+
        | Top right x position    | top_rx     |
        +-------------------------+------------+
        | Top right y position    | top_ry     |
        +-------------------------+------------+
        | Bottom right x position | bottom_rx  |
        +-------------------------+------------+
        | Bottom right y position | bottom_ry  |
        +-------------------------+------------+
        | Box width               | width      |
        +-------------------------+------------+
        | Box height              | height     |
        +-------------------------+------------+

        :rtype: boolean
        """

        def all_case(obj, kwargs):
            """
            Define DimBox points from all corners.

            X-------X
            |       |
            |       |
            X-------X

            Height and width are deduced

            rtype: pyscribus.dimensions.DimBox
            """

            tlx,tly = kwargs["top_lx"],kwargs["top_ly"]
            brx,bry = kwargs["bottom_rx"],kwargs["bottom_ry"]

            obj.dims["width"].value = brx - tlx
            obj.dims["height"].value = bry - tly

            obj.setx("top-right", brx)
            obj.sety("top-right", tly)
            obj.setx("top-left", tlx)
            obj.sety("top-left", tly)
            obj.setx("bottom-left", tlx)
            obj.sety("bottom-left", bry)
            obj.setx("bottom-right", brx)
            obj.sety("bottom-right", bry)

            return obj

        def from_tr(obj, kwargs):
            """
            Define DimBox points from top-right corner.

            <--------X
                     |
                     |
                     v

            rtype: pyscribus.dimensions.DimBox
            """

            # Troy to avoid using try and "tory".
            # I don’t care about UK parties.
            trox = float(kwargs["top_rx"])
            troy = float(kwargs["top_ry"])
            width = float(kwargs["width"])
            height = float(kwargs["height"])

            obj.dims["width"].value = width
            obj.dims["height"].value = height

            obj.setx("top-right", trox)
            obj.sety("top-right", troy)
            obj.setx("top-left", trox - width)
            obj.sety("top-left", troy)
            obj.setx("bottom-left", trox - width)
            obj.sety("bottom-left", troy + height)
            obj.setx("bottom-right", trox)
            obj.sety("bottom-right", troy + height)

            return obj

        def from_tl(obj, kwargs):
            """
            Define DimBox points from top-left corner.

            X------->
            |
            |
            v

            rtype: pyscribus.dimensions.DimBox
            """

            tlx = float(kwargs["top_lx"])
            tly = float(kwargs["top_ly"])
            width = float(kwargs["width"])
            height = float(kwargs["height"])

            obj.dims["width"].value = width
            obj.dims["height"].value = height

            obj.setx("top-left", tlx)
            obj.sety("top-left", tly)
            obj.setx("top-right", tlx + width)
            obj.sety("top-right", tly)
            obj.setx("bottom-left", tlx)
            obj.sety("bottom-left", tly + height)
            obj.setx("bottom-right", tlx + width)
            obj.sety("bottom-right", tly + height)

            return obj

        def check_case(kwargs, casename):
            """
            Check if there is any enough kwargs arguments to set the box
            according to a specific box setting scenario / case.

            :rtype: string,boolean
            :returns: casename or False
            """

            case = False

            if casename == "set_from_all":
                case =  ["top_lx", "top_ly", "bottom_rx", "bottom_ry"]

            if casename == "set_from_tl":
                case = ["top_lx", "top_ly", "width", "height"]

            if casename == "set_from_tr":
                case = ["top_rx", "top_ry", "width", "height"]

            if case:

                met = 0

                for k in case:
                    if k in kwargs:
                        met += 1

                if met == len(case):
                    return casename

            return False

        if kwargs is not None:
            case = False

            rotation_deg = False

            if "rotation" in kwargs:
                rotation_deg = kwargs["rotation"]

            # Setting from top left corner ?
            case = check_case(kwargs, "set_from_tl")

            if not case:
                # Setting from top right corner ?
                case = check_case(kwargs, "set_from_tr")

            if not case:
                # Setting from top left and bottom right corner
                case = check_case(kwargs, "set_from_all")

            if case:

                if case == "set_from_tl":
                    self = from_tl(self, kwargs)

                if case == "set_from_tr":
                    self = from_tr(self, kwargs)

                if rotation_deg:
                    self.rotated_coords = copy.deepcopy(self.coords)
                    self.rotate(rotation_deg)

                return True
            else:
                return False
        else:
            return False

    def resize_side(self, side, value):
        """
        Resize the box from a side.

        :type side: str
        :param side: Side of the box to resize from. 
            Must be "left", "right", "top", "bottom".
        :type value: float
        :param value: Resize value
        """

        if side in ["left", "right", "top", "bottom"]:

            if side in ["left", "right"]:
                self.dims["width"].value += value

            if side in ["top", "bottom"]:
                self.dims["height"].value += value

            if side == "left":
                nlx = self.getx("top-left") + value
                self.setx("top-left", nlx)
                self.setx("bottom-left", nlx)

            if side == "right":
                nrx = self.getx("top-right") + value
                self.setx("top-right", nrx)
                self.setx("bottom-right", nrx)

            if side == "top":
                nty = self.gety("top-left") + value
                self.sety("top-left", nty)
                self.sety("top-right", nty)

            if side == "bottom":
                nby = self.gety("bottom-left") + value
                self.sety("bottom-left", nby)
                self.sety("bottom-right", nby)

            return True
        else:
            return False

    def rotate(self, degree):
        """
        Rotate the box by degree.

        .. warning:: NOT IMPLEMENTED YET & DON'T KNOW HOW TO

        :type degree: float
        :param degree: Degree of rotation

        This method **don't** modify DimBox.coords but update
        DimBox.rotated_coords.
        """

        # FIXME TODO USE OF MATHEMATICAL BLACK MAGIC REQUIRED HERE
        #
        # Rotate all the points of self.rotated_coords by degree.
        #
        # In case you need to use radians (?) to implement that, please
        # keep in mind that Scribus use degrees as anyone sane and
        # practical do.
        #
        # NOTE It is crucial you don't modify Dim.coords, as in SLA
        # XML, only original box coords and rotation angle value
        # are saved.

        # FIXME Remove that after implementation
        print("PyScribus - Box rotation not implemented.")
        print("Rotation degree :", degree)

        valid = True

        if valid:
            self.rotation.value = degree

        return True

    #--- Python __ methods -----------------------------------------------

    def __eq__(self, other):
        for cname in self.coords.keys():

            for idx in [0,1]:
                a = self.coords[cname][idx].value
                b = other.coords[cname][idx].value

                if not a == b:
                    return False

        return True

    def __str__(self):
        return "X {} Y {} Width {} Height {}".format(
            self.coords["top-left"][0].value,
            self.coords["top-left"][1].value,
            self.dims["width"],
            self.dims["height"],
        )

# vim:set shiftwidth=4 softtabstop=4 spl=en:
