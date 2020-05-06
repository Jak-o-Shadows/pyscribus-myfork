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
PyScribus module for PDF & printing settings / elements.
"""

# Imports ===============================================================#

import collections

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions

from pyscribus.common.xml import *

import pyscribus.dimensions as dimensions

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class PDFSettings(PyScribusElement):
    """
    Class for PDF export settings in SLA
    """

    imgcomp_method_xml = {
        "automatic": 0, "jpeg": 1, "flate": 2, "none": 3
    }

    imgcomp_quality_xml = {
        "max": 0, "high": 1, "medium": 2, "low": 3, "min": 4
    }

    def __init__(self):
        super().__init__()

        self.lpi = []

        self.text_compression = True
        self.image_compression = {
            "method": "automatic",
            "quality": "max"
        }

        #-------------------------------------------------------

        # Flag, set to 1 when Presentation effects should be used
        PresentMode="0"

        #-------------------------------------------------------

        # Flag, set to 1 when Downsample Images is checked in the PDF-Options Dialog
        RecalcPic="0"
        # Resolution for downsampling Images
        PicRes="300"
        # Resolution for embedded EPS-Pictures or PDF's
        Resolution="300"

        #-------------------------------------------------------

        # (optional) Flag, set to 1 when Output should be in RGB
        RGBMode="1"

        # TODO : fromxml / toxml of this dict

        self.profiles = {
            "colors": {
                # (optional) Flag, set to 1 when ICC-Profiles should be used
                # for solid colours
                # UseProfiles="0"
                "used": False,
                # (optional) ICC-Profile for solid colours
                # SolidP="sRGB IEC61966-2.1"
                "name": "sRGB IEC61966-2.1"
            },
            "images": {
                # (optional) Flag, set to 1 when ICC-Profiles should be used
                # for images
                # UseProfiles2="0"
                "used": False,
                # ICC-Profile for images ?
                # ImageP="sRGB IEC61966-2.1"
                "name": "sRGB IEC61966-2.1"
            },
            "printer": {
                # (optional) ICC-Profile for the Printer, only used for 
                # PDF-X/3 output
                # PrintP="Fogra27L CMYK Coated Press"
                "name": "Fogra27L CMYK Coated Press"
            }
        }

        #-------------------------------------------------------

        self.bleeds = collections.OrderedDict()
        self.bleeds["top"] = dimensions.Dim(0),
        self.bleeds["left"] = dimensions.Dim(0),
        self.bleeds["right"] = dimensions.Dim(0),
        self.bleeds["bottom"] = dimensions.Dim(0),
        self.bleeds["document"] = False

        #-------------------------------------------------------

        bleedMarks="0"
        cropMarks="0"
        registrationMarks="0"
        colorMarks="0"
        docInfoMarks="0"
        markLength="20.0012598425197"
        markOffset="0"

        #-------------------------------------------------------

        self.encryption = {
            "pass": {"owner": "", "user": ""},
            "settings": {"permissions": "-4", "encrypted": False}
        }

        #-- FIXME Documented but to organize -------------------

        # (optional) Flag, set to 1 when the informations in the LPI tags should be used
        # for Linescreening
        UseLpi="0"
        # Binding for the PDF-Document 0 = Left Binding 1 = Right Binding
        Binding="0"
        # PDF-Version which should be generated 12 = PDF-X/3 13 = PDF-1.3 14 = PDF-1.4
        Version="14"
        # Flag, set to 1 when Generate Thumbnails is checked in the PDF-Options Dialog
        Thumbnails="0"
        # Flag, set to 1 when use PDF-Articles is checked in the PDF-Options Dialog
        Articles="0"
        # Flag, set to 1 when include Bookmarks is checked in the PDF-Options Dialog
        Bookmarks="0"

        #-- FIXME Undocumented, managed with undocumented funs -

        # ImagePr="0"
        # UseLayers="0"
        # UseSpotColors="1"
        # doMultiFile="0"
        # displayBookmarks="0"
        # displayFullscreen="0"
        # displayLayers="0"
        # displayThumbs="0"
        # hideMenuBar="0"
        # hideToolBar="0"
        # fitWindow="0"
        # openAfterExport="0"
        # PageLayout="0"
        # openAction=""
        # Intent="1"
        # Intent2="0"
        # InfoString=""
        # FontEmbedding="0"
        # Grayscale="0"
        # firstUse="1"
        # EmbedPDF="0"
        # MirrorH="0"
        # MirrorV="0"
        # Clip="0"
        # rangeSel="0"
        # rangeTxt=""
        # RotateDeg="0"

    def fromxml(self, xml):

        if xml.tag == "PDF":
            # TODO

            text_comp = xml.get("Compress")

            if text_comp is not None:
                self.text_compression = num_to_bool(text_comp)

            # Image compression : method and quality -----------

            for case in [
                    [xml.get("CMethod"), "method",
                    PDFSettings.imgcomp_method_xml],
                    [xml.get("Quality"), "quality",
                    PDFSettings.imgcomp_quality_xml]]:

                if (att := xml.get(case[0])) is not None:
                    if int(att) in case[2].values():
                        for human,code in case[2].items():
                            self.image_compression[case[1]] = human
                            break
                    else:
                        raise exceptions.InsaneSLAValue(
                            "Unknown image compression {}.".format(case[1])
                        )

            # Bleed settings -----------------------------------

            for case in ["top", "left", "right", "bottom"]:
                att_name = "B{}".format(case.capitalize())

                if (att := xml.get(att_name)) is not None:
                    self.bleeds[case][0].value = float(att)

            udb = xml.get("useDocBleeds")

            if udb is not None:
                self.bleeds["document"] = num_to_bool(udb)

            # PDF encryption settings---------------------------

            encrypt = xml.get("Encrypt")
            encrypt_perm = xml.get("Permissions")

            for case in [["owner", "PassOwner"], ["user", "PassUser"]]:
                if (attrib := xml.get(case[1])) is not None:
                    self.encryption["pass"][case[0]] = attrib

            if encrypt is not None:
                self.encryption["settings"]["encrypted"] = num_to_bool(encrypt)

            if encrypt_perm is not None:
                self.encryption["settings"]["permissions"] = encrypt_perm

            # Line per inch settings ---------------------------

            for element in xml:
                if element.tag == "LPI":
                    lo = LPI()
                    success = lo.fromxml(element)

                    if success:
                        self.lpi.append(lo)

            #--- FIXME This records undocumented attributes -------

            self.undocumented = undocumented_to_python(
                xml,
                [
                    "ImagePr", "UseLayers", "UseSpotColors", "doMultiFile",
                    "displayBookmarks", "displayFullscreen", "displayLayers",
                    "displayThumbs", "hideMenuBar", "hideToolBar", "fitWindow",
                    "openAfterExport", "PageLayout", "openAction", "Intent",
                    "Intent2", "InfoString", "FontEmbedding", "Grayscale",
                    "firstUse", "EmbedPDF", "MirrorH", "MirrorV", "Clip",
                    "rangeSel", "rangeTxt", "RotateDeg",
                ]
            )
        else:
            return False

        return True

    def toxml(self):
        xml = ET.Element("PDF")

        xml.attrib["Compress"] = bool_to_num(self.text_compression)

        xml.attrib["CMethod"] = str(
            PDFSettings.imgcomp_method_xml[self.image_compression["method"]]
        )

        xml.attrib["Quality"] = str(
            PDFSettings.imgcomp_quality_xml[self.image_compression["quality"]]
        )

        # Bleed settings -----------------------------------

        for bleed_config,bleed_value in self.bleeds.items():

            if bleed_config != "document":
                att_name = "B{}".format(bleed_config.capitalize())
                xml.attrib[att_name] = bleed_value[0].toxmlstr()

        xml.attrib["useDocBleeds"] = bool_to_num(self.bleeds["document"])

        # PDF encryption settings---------------------------

        xml.attrib["PassOwner"] = self.encryption["pass"]["owner"]
        xml.attrib["PassUser"] = self.encryption["pass"]["user"]
        xml.attrib["Permissions"] = self.encryption["settings"]["permissions"]
        xml.attrib["Encrypt"] = bool_to_num(
            self.encryption["settings"]["encrypted"]
        )

        # Line per Inch children ---------------------------

        for lo in self.lpi:
            lx = lo.toxml()

            if len(lx):
                xml.append(lx)

        #--- FIXME This exports undocumented attributes -------

        try:
            xml = undocumented_to_xml(xml, self.undocumented)
        except AttributeError:
            pass

        return xml

    def fromdefault(self):
        self.text_compression = True
        self.image_compression = {
            "method": "automatic",
            "quality": "max"
        }

        # Default line per each settings

        self.lpi = []

        for dlpi in LPI.DEFAULTS:
            l = LPI()
            l.fromdefault(dlpi[0])

            self.lpi.append(l)


class LPI(PyScribusElement):
    """
    Lines per Inch settings (LPI) in SLA
    """

    spot_xml = {
        "dot": "0",
        "line": "1",
        "round": "2",
        "ellipse": "3",
    }

    DEFAULTS = [
        ["Black", 133, 45, "ellipse"],
        ["Cyan", 133, 105, "ellipse"],
        ["Magenta", 133, 75, "ellipse"],
        ["Yellow", 133, 90, "ellipse"]
    ]

    def __init__(self):
        super().__init__()

        self.pyscribus_defaults = [l[0] for l in LPI.DEFAULTS]

        # Linescreening angle
        self.angle = dimensions.Dim(0, "deg")

        # Name of the Colour for which these settings are ment
        self.color = ""

        # How many lines per Inch are used
        self.frequency = dimensions.Dim(133, "lpi")

        # Code for the used Spotfunction
        self.spot = "ellipse"

    #--- PyScribus standard methods ----------------------------

    def fromdefault(self, default):

        if default in self.pyscribus_defaults:

            self.color = default

            for lpd in LPI.DEFAULTS:

                if lpd[0] == default:
                    self.frequency.value = lpd[1]
                    self.angle.value = lpd[2]

                    if lpd[3] in LPI.spot_xml:
                        self.spot = lpd[3]
                    else:
                        self.spot = "ellipse"

                    break

    def fromxml(self, xml):

        if xml.tag == "LPI":

            if (color := xml.get("Color")) is not None:
                self.color = color

            if (freq := xml.get("Frequency")) is not None:
                self.frequency.value = int(freq)

            if (angle := xml.get("Angle")) is not None:
                self.angle.value = float(angle)

            if (spot := xml.get("SpotFunction")) is not None:

                for human,code in LPI.spot_xml.items():
                    if code == spot:
                        self.spot = human
                        break

            return True
        else:
            return False

    def toxml(self):
        xml = ET.Element("LPI")

        xml.attrib["Color"] = self.color
        xml.attrib["Frequency"] = self.frequency.toxmlstr()
        xml.attrib["Angle"] = self.angle.toxmlstr()
        xml.attrib["SpotFunction"] = LPI.spot_xml[self.spot]

        return xml


class PrinterSettings(PyScribusElement):

    def __init__(self):
        super().__init__()

        self.mirror_pages = {
            "horizontal": False,
            "vertical": False
        }

        self.marks = {
            "crop": False,
            "bleed": False,
            "registration": False,
            "color": False
        }

        firstUse="1"

        # Print to file
        toFile="0"
        useAltPrintCommand="0"
        outputSeparations="0"

        # Whether to use spot colors
        useSpotColors="0"
        useColor="0"

        # Use ICC color profiles
        useICC="0"
        # Whether to have grey component replacement
        doGCR="0"

        doClip="0"
        setDevParam="0"

        includePDFMarks="0"

        # The postscrip level
        PSLevel="0"

        # Which printer description language
        PDLanguage="0"
        markLength="7.185302734375"
        markOffset="0"

        # --- Bleeds --------------------------------------------

        self.bleeds = collections.OrderedDict()
        self.bleeds["top"] = dimensions.Dim(0),
        self.bleeds["left"] = dimensions.Dim(0),
        self.bleeds["right"] = dimensions.Dim(0),
        self.bleeds["bottom"] = dimensions.Dim(0),
        self.bleeds["document"] = False

        # -------------------------------------------------------

        printer=""
        filename=""
        separationName=""
        printerCommand=""

    #--- PyScribus standard methods ----------------------------

    def fromxml(self, xml):

        if xml.tag == "Printer":

            # --- Page mirroring ------------------------------------

            if (mrh := xml.get("mirrorH")) is not None:
                self.mirror_pages["horizontal"] = num_to_bool(mrh)

            if (mrv := xml.get("mirrorV")) is not None:
                self.mirror_pages["vertical"] = num_to_bool(mrv)

            # --- Marks ---------------------------------------------

            for case in ["crop", "bleed", "registration", "color"]:
                att_name = "{}Marks".format(case)

                if (att := xml.get(att_name)) is not None:
                    self.marks[case] = num_to_bool(att)

            # --- Printer bleeds ------------------------------------

            for case in ["top", "left", "right", "bottom"]:
                att_name = "Bleed{}".format(case.capitalize())

                if (att := xml.get(att_name)) is not None:
                    self.bleeds[case][0].value = float(att)

            if (udb := xml.get("useDocBleeds")) is not None:
                self.bleeds["document"] = num_to_bool(udb)

            # -------------------------------------------------------

            # TODO

            return True
        else:
            return False

    def toxml(self):
        xml = ET.Element("Printer")

        # TODO

        for bleed_config,bleed_value in self.bleeds.items():

            if bleed_config != "document":
                att_name = "Bleed{}".format(bleed_config.capitalize())
                xml.attrib[att_name] = bleed_value[0].toxmlstr()

        xml.attrib["mirrorH"] = bool_to_num(self.mirror_pages["horizontal"])
        xml.attrib["mirrorV"] = bool_to_num(self.mirror_pages["vertical"])

        xml.attrib["useDocBleeds"] = bool_to_num(self.bleeds["document"])

        for k,v in self.marks.items():
            att_name = "{}Marks".format(k)

            xml.attrib[att_name] = bool_to_num(v)

        return xml

# vim:set shiftwidth=4 softtabstop=4 spl=en:
