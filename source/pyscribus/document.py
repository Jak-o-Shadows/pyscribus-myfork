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
Document classes
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions

from pyscribus.common.xml import *

import pyscribus.dimensions as dimensions
import pyscribus.colors as pscolors
import pyscribus.toc as toc
import pyscribus.marks as marks
import pyscribus.pages as pages
import pyscribus.styles as styles
import pyscribus.itemattribute as itemattribute
import pyscribus.patterns as patterns
import pyscribus.pageobjects as pageobjects
import pyscribus.notes as notes
import pyscribus.printing as printing

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class Document(PyScribusElement):
    """
    SLA Document (DOCUMENT) in SLA file.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: SLA parent instance
    """

    metadata_xml = {
        "AUTHOR": "author", "COMMENTS": "comments", "PUBLISHER": "publisher",
        "DOCDATE": "date", "DOCTYPE": "type", "DOCFORMAT": "format",
        "DOCIDENT": "identifier", "DOCSOURCE": "source", "DOCLANGINFO": "lang",
        "DOCRELATION": "related", "DOCCOVER": "cover", "DOCRIGHTS": "rights",
        "TITLE": "title", "SUBJECT": "subject", "DOCCONTRIB": "contributor"
    }

    ui_show_xml = {
        "SHOWMARGIN": "margins", "SHOWBASE": "baseline", "SHOWPICT": "images",
        "SHOWLINK": "links", "SHOWGRID": "grid", "SHOWGUIDES": "guides",
        "showcolborders": "colborders", "showrulers": "rulers"
    }

    bleed_xml = {
        "BleedTop": "top", "BleedRight": "right", "BleedLeft": "left",
        "BleedBottom": "bottom"
    }

    def __init__(self, sla_parent=False):
        super().__init__()

        self.sla_parent = sla_parent

        #-----------------------------------------------

        self.profiles = []
        self.pdf_settings = []
        self.printer_settings = []

        #-----------------------------------------------

        self.colors = []
        self.layers = []
        self.patterns = []
        self.gradients = []

        #-----------------------------------------------

        self.pages = []
        self.page_sets = []
        self.master_pages = []
        self.page_objects = []

        #-----------------------------------------------

        self.tocs = []
        self.marks = []
        self.sections = []

        #-----------------------------------------------

        self.page_number = 0

        # Page dimensions, borders, bleeds

        self.dims = {
            "width": dimensions.Dim(595.275590551181),
            "height": dimensions.Dim(841.889763779528)
        }

        self.borders = {
            "left": dimensions.Dim(40), "right": dimensions.Dim(40),
            "top": dimensions.Dim(40), "bottom": dimensions.Dim(40)
        }


        self.bleed = {
            "top": dimensions.Dim(0), "right": dimensions.Dim(0),
            "left": dimensions.Dim(0), "bottom": dimensions.Dim(0)
        }

        #-----------------------------------------------

        self.notes = []
        self.notes_frames = []

        self.styles = {
            "note": [],
            "paragraph": [],
            "character": [],
            "table": [],
            "cell": [],
        }

        #-----------------------------------------------

        self.attributes = []

        # ----------------------------------------------

        self.metadata = {
            "title": "", "author": "", "subject": "", "keywords": [],
            "comments": "", "publisher": "", "contributor": "",
            "date": "", "type": "", "format": "", "identifier": "",
            "source": "", "lang": "", "related": "", "cover": "",
            "rights": "",
        }

        #--- ICC color profiles ------------------------

        self.icc_profiles = {
            "rgb_images": "", "cmyk_images": "",
            "rgb_colors": "", "cmyk_colors": "",
            "printer": "",
        }

        # ----------------------------------------------

        self.ui_snapping = {"guides": False, "grid": False, "element": False}

        # ----------------------------------------------

        self.ui_show = {
            "margins": True,
            "baseline": False,
            "images": True,
            "links": False,
            "grid": False,
            "guides": True,
            "colborders": True,
            "rulers": True
        }

        # ----------------------------------------------

        self.calligraphicpen = {
            "angle": dimensions.Dim(0, "cdeg", True),
            "line_width": dimensions.Dim(0, "pica"),
            "line_shade": dimensions.Dim(100, "perc", True),
            "line_color": "",
            "width": dimensions.Dim(0, "pica"),
            "style": "1",
            "fill_color": "",
            "fill_shade": dimensions.Dim(100, "perc", True),
        }

        #--- FIXME Not documented ----------------------
        # PRESET="0"

        # FIXME ---- À faire ---------------------------

        # (optional) Orientation of the Doc 0 = Portrait 1 = Landscape
        ORIENTATION="0"
        # Default page name, such as "A4" or "Letter"
        PAGESIZE="A4"
        # (optional) First page number in the Doc
        FIRSTNUM="1"
        # (optional) Which PageSet to use
        BOOK="0"

        # Number of Columns in automatic Textframes
        AUTOSPALTEN="1"
        # Distance between Columns in automatic Textframes
        ABSTSPALTEN="11"

        # (optional) Measurement unit for the Doc
        # 0 = Points 1 = Millimeters 2 = Inches 3 = Picas
        UNITS="1"

        # Default Font
        DFONT="Arial Regular"
        # Default Fontsize
        DSIZE="12"

        # (optional) Number of Columns in Textframes
        DCOL="1"
        # (optional) Default Gap between Columns in Textframes
        DGAP="0"

        #--- FIXME Not documented ----------------------
        # TabFill=""

        # Default width for tabs in text frames
        TabWidth="36"

        #--- FIXME Not documented ----------------------
        # TextDistLeft="0"
        # TextDistRight="0"
        # TextDistBottom="0"
        # TextDistTop="0"

        # FIXME ---- À faire ---------------------------

        # Percentage for Superscript
        VHOCH="33"
        # Percentage for scaling of the Glyphs in Superscript
        VHOCHSC="66"
        # Percentage for Subscript
        VTIEF="33"
        # Percentage for scaling of the Glyphs in Subscript
        VTIEFSC="66"
        # Percentage for scaling of the Glyphs in Small Caps
        VKAPIT="75"

        # (optional) Width of the Baseline Grid
        BASEGRID="14.4"
        # (optional) Startoffset for the Baseline Grid
        BASEO="0"

        #--- FIXME Not documented ----------------------
        # AUTOL="100"
        # UnderlinePos="-1"
        # UnderlineWidth="-1"
        # StrikeThruPos="-1"
        # StrikeThruWidth="-1"

        # (optional) Counter for Groups in the Doc
        GROUPC="1"
        # (optional) Colormanagement available 0 = off, 1 = on
        HCMS="0"
        # (optional) Simulate the Printer on Screen 0 = off, 1 = on
        DPSo="0"

        #--- FIXME Not documented ----------------------
        # DPSFo="0"

        # (optional) Use Colormanagement 0 = off, 1 = on
        DPuse="0"
        # (optional) Mark Colors out of Gamut 0 = off, 1 = on
        DPgam="0"
        # (optional) Use Blackpoint Compensation 0 = off, 1 = on
        DPbla="1"

        #--- FIXME Not documented ----------------------
        # DISc="1"
        # DIIm="0"

        # (optional) Active Layer
        ALAYER="0"

        # (optional) Language of the Doc
        LANGUAGE="fr"
        # (optional) Automatic Hyphenation 0 = off, 1 = on
        AUTOMATIC="1"
        # (optional) Automatic Hyphenation during typing 0 = off, 1 = on
        AUTOCHECK="0"
        # (optional) Guides locked 0 = off, 1 = on
        GUIDELOCK="0"

        # FIXME ---- À faire ---------------------------

        # (optional) Distance of the minor Gridlines
        MINGRID="20"
        # (optional) Distance of the major Gridlines
        MAJGRID="100"

        #--- FIXME Not documented ----------------------
        # SHOWFRAME="1"
        # SHOWControl="0"
        # SHOWLAYERM="0"

        # FIXME ---- À faire ---------------------------

        #--- FIXME Not documented ----------------------
        # rulerMode="1"

        #--- FIXME Not documented ----------------------
        # showBleed="1"
        # rulerXoffset="0"
        # rulerYoffset="0"
        # GuideRad="10"
        # GRAB="4"
        # POLYC="4"
        # POLYF="0.5"
        # POLYR="0"
        # POLYIR="0"
        # POLYCUR="0"
        # POLYOCUR="0"
        # POLYS="0"
        # arcStartAngle="30"
        # arcSweepAngle="300"
        # spiralStartAngle="0"
        # spiralEndAngle="1080"
        # spiralFactor="1.2"
        # AutoSave="1"
        # AutoSaveTime="600000" # milisec ?
        # AutoSaveCount="1"
        # AutoSaveKeep="0"
        # AUtoSaveInDocDir="1"
        # AutoSaveDir=""

        # Space at the bottom of the scratch space, after the last page
        ScratchBottom="20"
        # Space at the left of the scratch space
        ScratchLeft="100"
        # Space at the right of the scratch space
        ScratchRight="100"
        # Space at the top of the scratch space, before the pages
        ScratchTop="20"

        #--- FIXME Not documented ----------------------
        # GapHorizontal="0"
        # GapVertical="40"
        # StartArrow="0"
        # EndArrow="0"
        # PEN="Black"
        # BRUSH="None"
        # PENLINE="Black"
        # PENTEXT="Black"
        # StrokeText="Black"
        # TextBackGround="None"
        # TextLineColor="None"
        # TextBackGroundShade="100"
        # TextLineShade="100"
        # TextPenShade="100"
        # TextStrokeShade="100"
        # STIL="1"
        # STILLINE="1"
        # WIDTH="1"
        # WIDTHLINE="1"
        # PENSHADE="100"
        # LINESHADE="100"
        # BRUSHSHADE="100"
        # CPICT="None"
        # PICTSHADE="100"
        # CSPICT="None"
        # PICTSSHADE="100"
        # PICTSCX="1"
        # PICTSCY="1"
        # PSCALE="1"
        # PASPECT="1"
        # EmbeddedPath="0"
        # HalfRes="1"
        # dispX="10"
        # dispY="10"
        # constrain="15"

        # MINORC="#00ff00"
        # MAJORC="#00ff00"
        # GuideC="#000080"
        # BaseC="#c0c0c0"

        # Scribus GUI Page background
        PAGEC="#ffffff"

        # MARGC="#0000ff"

        # renderStack="2 0 4 1 3"
        # GridType="0"
        # RANDF="0"

        # currentProfile="PDF 1.4"


        # ----------------------------------------------

    #=== Setting defaults methods ===========================================

    def _default_profiles(self):
        """
        Add default checking profiles.
        """

        for def_name in Profile.defaults:
            self.profiles.append(Profile(default=def_name))

    def _default_layer(self):
        """
        Add default layer.
        """
        self.layers.append(Layer(default=True))

    def _default_layers(self):
        """
        Add default checking profiles.

        Alias for add_default_layer()
        """

        self._default_layer()

    def _default_snapping(self):
        """
        Set default UI snapping options.
        """

        self.ui_snapping = {"guides": True, "grid": False, "element": True}

    def _default_note_style(self):
        ns = styles.NoteStyle()
        ns.fromdefault()

        self.styles["note"].append(ns)

    def _default_note_styles(self):
        self._default_note_style()

    def _default_pages(self):
        """
        Add default page.
        """

        page = pages.Page()
        page.fromdefault()
        self.pages.append(page)

        return True

    def _default_page(self):
        """
        Alias of default_pages()

        .. sealso: default_pages()
        """

        self._default_pages()

    def _default_icc(self):
        """
        Set default ICC colors profiles.
        """
        self.icc_profiles = {
            "rgb_images": "sRGB display profile (ICC v2.2)",
            "cmyk_images": "ISO Coated v2 300% (basICColor)",
            "rgb_colors": "sRGB display profile (ICC v2.2)",
            "cmyk_colors": "ISO Coated v2 300% (basICColor)",
            "printer": "ISO Coated v2 300% (basICColor)",
        }

    def _default_ui_show(self):
        """
        Set default UI view options.
        """

        self.ui_show = {
            "margins": True,
            "baseline": False,
            "images": True,
            "links": False,
            "grid": False,
            "guides": True,
            "colborders": True,
            "rulers": True
        }

    def _default_calligraphic_pen(self):
        """
        Set default calligraphic pen options.
        """

        self.calligraphicpen = {
            "angle": dimensions.Dim(0, "cdeg", True),
            "line_width": dimensions.Dim(0, "pica"),
            "line_shade": dimensions.Dim(100, "perc", True),
            "line_color": "",
            "width": dimensions.Dim(0, "pica"),
            "style": 1,
            "fill_color": "",
            "fill_shade": dimensions.Dim(100, "perc", True),
        }

    def _default_pagesets(self):
        """
        Set default page sets.
        """

        self.page_sets = []

        for default in ["Single Page", "Facing Pages", "3-Fold", "4-Fold"]:
            ps = pages.PageSet()

            if (success := ps.fromdefault(default)):
                self.page_sets.append(ps)

    def _default_colors(self):
        """
        Set default colors.
        """

        for default in [
            "Black", "Blue", "Cool Black", "Cyan", "Green", "Magenta", "Red",
            "Registration", "Rich Black", "Warm Black", "White", "Yellow"]:

            co = pscolors.Color()
            success = co.fromdefault(default)

            if success:
                self.colors.append(co)

    def _default_pdfsettings(self):
        """
        Add default PDF settings.
        """

        pdf = printing.PDFSettings()
        pdf.fromdefault()
        self.pdf_settings = [pdf]

    def _default_section(self):
        """
        Alias of default_sections()

        .. sealso: default_section()
        """

        self.default_sections()

    def _default_sections(self):
        """
        Add default section.
        """

        sec = toc.Section()
        sec.fromdefault()
        self.sections = [sec]

    def _default_paragraph_styles(self):
        self.styles["paragraph"].append(
            styles.ParagraphStyle(self, default=True)
        )
        self.styles["paragraph"][-1].is_default = True

    def _default_character_styles(self):
        self.styles["character"].append(
            styles.CharacterStyle(self, default=True)
        )
        self.styles["character"][-1].is_default = True

    def fromdefault(self, default="all"):
        """
        Set default settings from a default list

        :param default: Set of default settings or list of default features to set.
        :type default: str,list

        Unlike other fromdefault() methods, Document.fromdefault() default
        parameter can only be "all" or a list of default features to set.

        +-------------------------+-------------------+
        | Default feature         | String            |
        +=========================+===================+
        | Colors                  | colors            |
        +-------------------------+-------------------+
        | Checking profiles       | profiles          |
        +-------------------------+-------------------+
        | Layers                  | layers            |
        +-------------------------+-------------------+
        | UI snapping             | uisnapping        |
        +-------------------------+-------------------+
        | Notes' styles           | nstyles           |
        +-------------------------+-------------------+
        | Paragraph styles        | pstyles           |
        +-------------------------+-------------------+
        | Character styles        | pstyles           |
        +-------------------------+-------------------+
        | Page                    | page, pages       |
        +-------------------------+-------------------+
        | ICC profiles            | icc               |
        +-------------------------+-------------------+
        | UI show                 | uishow            |
        +-------------------------+-------------------+
        | Calligraphic pen        | cpen              |
        +-------------------------+-------------------+
        | Page sets               | pagesets          |
        +-------------------------+-------------------+
        | PDF settings            | pdf               |
        +-------------------------+-------------------+
        | Document sections       | section, sections |
        +-------------------------+-------------------+

        For example, to create a SLA document with default colors, layers,
        but without any other defined defaults :

            fromdefault(["colors", "layers"])
        """

        features = {
            "colors": self._default_colors,
            "cpen": self._default_calligraphic_pen,
            "icc": self._default_icc,
            "layers": self._default_layers,
            "nstyles": self._default_note_styles,
            "pstyles": self._default_paragraph_styles,
            "cstyles": self._default_character_styles,
            "page": self._default_page,
            "pagesets": self._default_pagesets,
            "pdf": self._default_pdfsettings,
            "profiles": self._default_profiles,
            "section": self._default_sections,
            "uisnapping": self._default_snapping,
            "uishow": self._default_ui_show,
        }

        plurals = {
            "pages": "page",
            "sections": "section"
        }

        seq = []

        if default == "all":
            seq = features.keys()
        else:
            for f in default:

                f = f.lower()

                if f in features:
                    seq.append(f)

                else:

                    if f in plurals:
                        seq.append(plurals[f])

        for f in seq:
            features[f]()

    #========================================================================

    def fromxml(self, xml):
        # --- DOCUMENT attributes ----------------------------------------
        # TODO DOCUMENT many attribs…

        # Metadatas

        for att, key in Document.metadata_xml.items():
            if (v := xml.get(att)) is not None:
                self.metadata[key] = v

        # UI snapping

        for snap_thing in ["grid", "guides", "element"]:
            att_name = "SnapTo{}".format(snap_thing.capitalize())

            if (att := xml.get(att_name)) is not None:
                self.ui_snapping[snap_thing] = num_to_bool(att)

        # Bleed settings

        for att,human in Document.bleed_xml.items():
            if (att_value := xml.get(att)) is not None:
                self.bleed[human] = float(att_value)

        # UI show

        for att_name, ui_name in Document.ui_show_xml.items():
            if (att := xml.get(att_name)) is not None:
                self.ui_show[ui_name] = num_to_bool(att)

        # ICC color profiles

        for case in [
            ["DPIn", "rgb_images"], ["DPInCMYK", "cmyk_images"],
            ["DPIn2", "rgb_colors"], ["DPIn3", "cmyk_colors"],
            ["DPPr", "printer"]]:
            att_name,icc_key = case

            if (att := xml.get(att_name)) is not None:
                self.icc_profiles[icc_key] = att

        # Calligraphic pen

        for case in [
                ["Angle", "angle"], ["LineColorShade", "line_shade"],
                ["FillColorShade", "fill_shade"]]:
            att_name = "calligraphicPen{}".format(case[0])

            if (att := xml.get(att_name)) is not None:
                self.calligraphicpen[case[1]].value = int(att)

        for case in [["LineWidth", "line_width"], ["Width", "width"]]:
            att_name = "calligraphicPen{}".format(case[0])

            if (att := xml.get(att_name)) is not None:
                self.calligraphicpen[case[1]].value = float(att)

        for case in [
                ["LineColor", "line_color"], ["FillColor", "fill_color"],
                ["PenStyle", "style"]]:

            att_name = "calligraphicPen{}".format(case[0])

            if (att := xml.get(att_name)) is not None:
                self.calligraphicpen[case[1]] = att

        # --- DOCUMENT childs --------------------------------------------

        for child in xml:

            if child.tag == "CheckProfile":
                p = Profile()

                if (success := p.fromxml(child)):
                    self.profiles.append(p)

            if child.tag == "Gradient":
                gr = pscolors.Gradient()

                if (success := gr.fromxml(child)):
                    self.gradients.append(gr)

            if child.tag == "COLOR":
                c = pscolors.Color()

                if (success := c.fromxml(child)):
                    self.colors.append(c)

            if child.tag == "Pattern":
                patt = patterns.Pattern()

                if (success := patt.fromxml(child)):
                    self.patterns.append(patt)

            # TODO FIXME hyphen

            if child.tag in ["STYLE", "CHARSTYLE"]:

                if child.tag == "STYLE":
                    key,xstyle = "paragraph",styles.ParagraphStyle(self)

                if child.tag == "CHARSTYLE":
                    key,xstyle = "character",styles.CharacterStyle(self)

                if (success := xstyle.fromxml(child)):
                    self.styles[key].append(xstyle)

            if child.tag == "TableStyle":
                tstyle = styles.TableStyle(self)

                if (success := tstyle.fromxml(child)):
                    self.styles["table"].append(tstyle)

            if child.tag == "CellStyle":
                cstyle = styles.CellStyle(self)

                if (success := cstyle.fromxml(child)):
                    self.styles["cell"].append(cstyle)

            if child.tag == "LAYERS":
                l = Layer()

                if (success := l.fromxml(child)):
                    self.layers.append(l)

            if child.tag == "Printer":

                ps = printing.PrinterSettings()

                if (success := ps.fromxml(child)):
                    self.printer_settings.append(ps)

            if child.tag == "PDF":

                pds = printing.PDFSettings()

                if (success := pds.fromxml(child)):
                    self.pdf_settings.append(pds)

            if child.tag == "DocItemAttributes":

                for attribute in child:
                    da = itemattribute.DocumentAttribute()

                    if (success := da.fromxml(attribute)):
                        self.attributes.append(da)

            if child.tag == "TablesOfContents":

                for sub in child:

                    if sub.tag == "TableOfContents":
                        toc_settings = toc.TOC()

                        if (success := toc_settings.fromxml(sub)):
                            self.tocs.append(toc_settings)

            if child.tag == "Marks":

                for sub in child:

                    if sub.tag == "Mark":
                        mx = marks.DocumentMark()

                        if (success := mx.fromxml(sub)):
                            self.marks.append(mx)

            if child.tag == "NotesStyles":

                for sub in child:

                    if sub.tag == "notesStyle":
                        s = styles.NoteStyle()

                        if (success := s.fromxml(sub)):
                            self.styles["note"].append(s)

            if child.tag == "NotesFrames":

                for sub in child:

                    if sub.tag == "FOOTNOTEFRAME":
                        nf = notes.NoteFrame()

                        if (success := nf.fromxml(sub)):
                            self.notes_frames.append(nf)

            if child.tag == "Notes":

                for sub in child:

                    if child.tag == "Note":
                        nc = notes.Note()

                        if (success := nc.fromxml(sub)):
                            self.notes.append(nc)

            if child.tag == "PageSets":

                for page_set in child:
                    ps = pages.PageSet()

                    if (success := ps.fromxml(page_set)):
                        self.page_sets.append(ps)

            if child.tag == "Sections":

                for sub in child:

                    if sub.tag == "Section":
                        sec = toc.Section()

                        if (success := sec.fromxml(sub)):
                            self.sections.append(sec)

            if child.tag == "MASTERPAGE":
                m = pages.MasterPage()

                if (success := m.fromxml(child)):
                    self.master_pages.append(m)

            if child.tag == "PAGE":
                p = pages.Page()

                p.sla_parent = self.sla_parent
                p.doc_parent = self

                if (success := p.fromxml(child)):
                    self.pages.append(p)

            if child.tag == "PAGEOBJECT":
                ptype = child.get("PTYPE")

                if ptype is not None:

                    try:
                        po = pageobjects.new_from_type(
                            ptype, self.sla_parent, self
                        )

                        if (success := po.fromxml(child)):
                            self.page_objects.append(po)

                    except ValueError:
                        pass

        # ----------------------------------------------------------------

        return True

    def toxml(self, optional=True):
        xml = ET.Element("DOCUMENT")

        # --- DOCUMENT attributes ----------------------------------------

        # TODO DOCUMENT many attribs…

        # Bleed settings

        for att,human in Document.bleed_xml.items():
            xml.attrib[att] = str(self.bleed[human])

        xml.attrib["ANZPAGES"] = str(self.page_number)

        # Dimensions

        xml.attrib["PAGEWIDTH"] = self.dims["width"].toxmlstr()
        xml.attrib["PAGEHEIGHT"] = self.dims["height"].toxmlstr()

        # Borders

        for b in self.borders.keys():
            att = "BORDER{}".format(b.upper())
            xml.attrib[att] = self.borders[b].toxmlstr()

        # Metadatas

        for att, key in Document.metadata_xml.items():
            xml.attrib[att] = self.metadata[key]

        xml.attrib["KEYWORDS"] = "; ".join(self.metadata["keywords"])

        # UI snapping

        for k,v in self.ui_snapping.items():
            att = "SnapTo{}".format(k.capitalize())

            xml.attrib[att] = bool_to_num(v)

        # UI show

        for att_name, ui_name in Document.ui_show_xml.items():
            xml.attrib[att_name] = bool_to_num(self.ui_show[ui_name])

        # ICC profiles

        xml.attrib["DPIn"] = self.icc_profiles["rgb_images"]
        xml.attrib["DPInCMYK"] = self.icc_profiles["cmyk_images"]
        xml.attrib["DPIn2"] = self.icc_profiles["rgb_colors"]
        xml.attrib["DPIn3"] = self.icc_profiles["cmyk_colors"]
        xml.attrib["DPPr"] = self.icc_profiles["printer"]

        # Calligraphic pen
        # -------------------------------------------------

        for case in [
                ["Angle", "angle", True],
                ["LineWidth", "line_width", True],
                ["LineColorShade", "line_shade", True],
                ["LineColor", "line_color", False],
                ["Width", "width", True],
                ["Style", "style", False],
                ["FillColor", "fill_color", False],
                ["FillColorShade", "fill_shade", True]]:

            att_name = "calligraphicPen{}".format(case[0])
            att_value = self.calligraphicpen[case[1]]

            if case[2]:
                att_value = att_value.toxmlstr()

            if case[0] == "Style":
                att_value = str(att_value)

            xml.attrib[att_name] = att_value

        # --- DOCUMENT childs --------------------------------------------

        # Checking profiles -------------------------------

        for profile in self.profiles:
            px = profile.toxml()

            if not isinstance(px, bool):
                xml.append(px)

        # Colors ------------------------------------------

        for color in self.colors:
            cx = color.toxml()
            xml.append(cx)

        # TODO hyphen

        # Styles ------------------------------------------

        for pstyle in self.styles["paragraph"]:
            pstylex = pstyle.toxml()
            xml.append(pstylex)

        for cstyle in self.styles["character"]:
            cstylex = cstyle.toxml()
            xml.append(cstylex)

        for tstyle in self.styles["table"]:
            tstylex = tstyle.toxml()
            xml.append(tstylex)

        for cstyle in self.styles["cell"]:
            cstylex = cstyle.toxml()
            xml.append(cstylex)

        # Layers ------------------------------------------

        for layer in self.layers:
            layerx = layer.toxml()
            xml.append(layerx)

        # Printer settings --------------------------------

        for ps in self.printer_settings:
            px = ps.toxml()
            xml.append(px)

        # PDF settings ------------------------------------

        for pds in self.pdf_settings:
            px = pds.toxml()
            xml.append(px)

        # Document attributes -----------------------------

        doca = ET.Element("DocItemAttributes")

        for attribute in self.attributes:
            ax = attribute.toxml()
            doca.append(ax)

        xml.append(doca)

        # Tables of contents ------------------------------

        tocx = ET.Element("TablesOfContents")

        for toc in self.tocs:
            tx = toc.toxml()
            tocx.append(tx)

        xml.append(tocx)

        # Marks -------------------------------------------

        if self.marks:

            marksx = ET.Element("Marks")

            for m in self.marks:
                mx = m.toxml()
                marksx.append(mx)

            xml.append(marksx)

        # Notes : styles, frames, notes content -----------

        # Notes styles -------------------------------

        nsx = ET.Element("NotesStyles")

        for note_style in self.styles["note"]:
            nx = note_style.toxml()
            nsx.append(nx)

        xml.append(nsx)

        # Notes frames -------------------------------

        if self.notes_frames:

            nfx = ET.Element("NotesFrames")

            for note_frame in self.notes_frames:
                n = note_frame.toxml()
                nfx.append(n)

            xml.append(nfx)

        # Notes content ------------------------------

        if self.notes:

            nx = ET.Element("Notes")

            for note in self.notes:
                # n = note.toxml()
                # nx.append(n)
                pass

            xml.append(nx)

        # Page sets ---------------------------------------

        pssx = ET.Element("PageSets")

        for page_set in self.page_sets:
            px = page_set.toxml()
            pssx.append(px)

        xml.append(pssx)

        # Sections ----------------------------------------

        secx = ET.Element("Sections")

        for section in self.sections:
            sx = section.toxml()
            secx.append(sx)

        xml.append(secx)

        # Master pages ------------------------------------

        for master in self.master_pages:
            mx = master.toxml()
            xml.append(mx)

        # Pages -------------------------------------------

        for page in self.pages:
            p = page.toxml()
            xml.append(p)

        # Pages objects -----------------------------------

        for po in self.page_objects:
            px = po.toxml()
            xml.append(px)

        # ----------------------------------------------------------------

        return xml

    #========================================================================

    def pageobjects(self, object_type=False, templatable=False):
        pos_ret = []

        # If there is a object type filter, we filter before checking
        # if we must return only templatable objects

        if object_type:

            if object_type in pageobjects.po_type_classes:
                pos = []

                for po in self.page_objects:
                    if isinstance(po, pageobjects.po_type_classes[object_type]):
                        pos.append(po)

        if templatable:

            if self.sla_parent.templating["active"]:
                lookup_set = []
                templatable_set = []

                if object_type:
                    lookup_set = pos
                else:
                    lookup_set = self.page_objects

                for po in lookup_set:
                    # If the page object is a text frame with templatable
                    # stories, we add these templatable stories

                    if isinstance(po, pageobjects.TextObject):
                        po_templatable_stories = po.templatable()

                        if po_templatable_stories:
                            templatable_set.extend(po_templatable_stories)

                    else:
                        # TODO If this page object is another type of page
                        # object, we look its properties and find if it 
                        # is templatable through sla.SLA.templating settings

                        if po.templatable():
                            templatable_set.append(po)

                pos_ret = templatable_set

        else:
            if object_type:
                pos_ret = pos
            else:
                pos_ret = self.page_objects

        return pos_ret

    def stories(self):
        """
        Returns all stories in the document.

        :rtype: list
        :returns: List of stories
        """

        stories = []

        #--- Text frames stories -----------------------------------------

        filtered = [
            po for po in self.page_objects if po.have_stories and po.stories
        ]

        if filtered:

            for po in filtered:
                stories.extend(po.stories)

        #--- Table cells stories -----------------------------------------

        tables = [
            po for po in self.page_objects if po.ptype == "table"
        ]

        if tables:
            cells = []

            for po in tables:
                cells.extend(po.cells)

            for cell in cells:
                if cell.story is not None:
                    stories.append(cell.story)

        #-----------------------------------------------------------------

        return stories

    #========================================================================

    def page_number(self):
        """
        Get document pages number.
        """

        pn = 0

        for p in self.pages:
            if po.number > pn:
                pn = po.number

        return pn

    def append(self, sla_object, **kwargs):
        """
        Append a page, a page object, layer, style…

        +----------------+---------+-----------------------------------------+
        | Argument name  | Type    | Usage                                   |
        +================+=========+=========================================+
        | check_color    | boolean | If True, check if a document's color    |
        |                |         | already have the same inks as           |
        |                |         | sla_object.                             |
        +----------------+---------+-----------------------------------------+
        | overlap_object | boolean | If True (default) and if sla_object is  |
        |                |         | a page object, sla_object will be added |
        |                |         | even if its coordinates overlap with a  |
        |                |         | document's page object coordinates.     |
        |                |         |                                         |
        |                |         | If False, coordinates of sla_object     |
        |                |         | will be checked against document's page |
        |                |         | objects, and eventually raise           |
        |                |         | OverlappingPageObject.                  |
        +----------------+---------+-----------------------------------------+
        | overlap_layer  | boolean | If True (default) AND overlap_object is |
        |                |         | False, sla_object page object           |
        |                |         | coordinates will only be checked        |
        |                |         | against document's page objects on the  |
        |                |         | same layer.                             |
        +----------------+---------+-----------------------------------------+

        :param kwargs: dict
        :type kwargs: Appending options
        :rtype: boolean
        :returns: True if appending succeed
        """

        # TODO On pourra rajouter des tests ici.
        # Par exemple, si l’objet ajouté n’entre pas en collision
        # avec un autre du même calque, etc.

        if isinstance(sla_object, pageobjects.PageObject):
            if "overlap_object" in kwargs:
                overlap = kwargs["overlap_object"]
            else:
                overlap = True

            add = False

            if overlap:
                add = True
            else:
                if "overlap_layer" in kwargs:
                    same_layer = kwargs["overlap_layer"]
                else:
                    same_layer = True

                if same_layer:
                    page_objets = [
                        po for po in self.page_objets
                        if po.layer == sla_object.layer
                    ]
                else:
                    page_objets = self.page_objects

                for po in page_objets:
                    # TODO FIXME Test coordinates

                    # TODO If coordinates overlaps:
                    # add = False
                    # break

                    pass

            if add:
                sla_object.doc_parent = self
                sla_object.sla_parent = self.sla_parent

                self.page_objects.append(sla_object)

                return True
            else:
                return False

        if isinstance(sla_object, pages.PageAbstract):
            # NOTE If sla_object is a page or a master page, its number
            # attribute is only relevant if there is a page number gap.

            # TODO Obtenir les numéros de page actuellement utilisés,
            # puis vérifier s’il y a des pages manquantes.

            page_gaps = []
            page_numbers = sorted([i.number for i in self.pages])
            max_page = page_numbers[-1]

            # TODO FIXME Pas convaincu par cette manière de retrouver
            # les numéros de page manquants.

            last_num = 1
            for num in range(1, max_page + 1):
                idx = num - 1

                if num == 1:
                    if page_numbers[idx] != 1:
                        page_gaps.append(num)

                else:
                    if page_numbers[idx] != last_num + 1:
                        page_gaps.append(num)

                last_num += 1

            # Si le numéros de page de sla_object correspond à une page
            # manquante:
            #   - on ajoute sla_object sans modifier son numéro de page
            #   via insert(index_manquant, sla_object)
            #
            # Si le numéro de page de sla_object ne correspond pas à une
            # page manquante ou n’a aucun putain de sens:
            #   - on définit le numéro de page de sla_object comme étant
            #   le plus grand numéro de page actuel + 1,
            #   - on ajoute via append()

            sla_object.doc_parent = self
            sla_object.sla_parent = self.sla_parent

            if isinstance(sla_object, pages.Page):
                self.pages.append(sla_object)
                return True

            if isinstance(sla_object, pages.MasterPage):
                self.master_pages.append(sla_object)
                return True

        if isinstance(sla_object, Layer):

            for layer in self.layers:

                # If a layer have the same level

                if layer.level == sla_object.level:
                    raise exceptions.ConflictingLayer(
                        "Layer on level {} already exists".format(
                            sla_object.layer
                        )
                    )

                # If a layer have the same name

                if layer.name == sla_object.name:
                    raise exceptions.ConflictingLayer(
                        "Layer with name '{}' already exists".format(
                            sla_object.name
                        )
                    )

            self.layers.append(sla_object)

            return True

        if isinstance(sla_object, pscolors.Color):
            # NOTE check_color can be set to False, as the user might want
            # to use colors with different names, but same colors as a part
            # of his/her graphical chart / layer.

            if "check_color" in kwargs:
                check = kwargs["check_color"]
            else:
                check = False

            if check:
                add = True

                for color in self.colors:
                    if color == sla_object:
                        add = False
                        break

                if add:
                    self.colors.append(sla_object)

                    return True

            else:
                self.colors.append(sla_object)

                return True

        if isinstance(sla_object, styles.StyleAbstract):

            if isinstance(sla_object, styles.NoteStyle):
                self.styles["note"].append(sla_object)
                return True

            else:
                sla_object.doc_parent = self
                # TODO NOTE Maybe we should add a call to a StyleAbstract
                # "hook" for a "added to document" event, to manage style
                # parents. Something like :
                # sla_object.event("added-to-document")

                if isinstance(sla_object, styles.ParagraphStyle):
                    self.styles["paragraph"].append(sla_object)
                    return True

                if isinstance(sla_object, styles.CharacterStyle):
                    self.styles["character"].append(sla_object)
                    return True

                # TODO NOTE Then we should call a "hook" to all styles that
                # may have parents styles to update them as well.
                # Something like :
                # for paragraph_style in self.styles["paragraph"]:
                    # if isinstance(sla_object, styles.CharacterStyle):
                        # paragraph_style.event("charstyle-added-document")
                    # if isinstance(sla_object, styles.ParagraphStyle):
                        # paragraph_style.event("parastyle-added-document")

        return False

    #========================================================================


class Profile(PyScribusElement):
    """
    """

    defaults = [
        "PDF 1.3", "PDF 1.4", "PDF 1.5", "PDF/X-3", "PDF/X-4", "PostScript", "PDF/X-1a"
    ]

    def __init__(self, default=False):
        super().__init__()

        self.pyscribus_defaults = [k for k in Profile.defaults]

        self.name = ""

        self.checks = {
            "auto": False,
            "Glyphs": False,
            "Orphans": False,
            "Overflow": False,
            "Pictures": False,
            "PartFilledImageFrames": False,
            "Resolution": False,
            "Transparency": False,
            "Annotations": False,
            "RasterPDF": False,
            "ForGIF": False,
            "NotCMYKOrSpot": False,
            "DeviceColorsAndOutputIntent": False,
            "FontNotEmbedded": False,
            "FontIsOpenType": False,
            "AppliedMasterDifferentSide": False,
            "EmptyTextFrames": False
        }

        self.ignores = {"Errors": False, "OffLayers": False}

        self.resolution = {
            "min": dimensions.Dim(0, "dpi", True),
            "max": dimensions.Dim(0, "dpi", True)
        }

        if default:
            self.fromdefault(default)

    def set_checks(self, checks, value=True):
        """
        :param checks: List of checks names
        :type checks: list
        :param value: –
        :type value: –
        """
        for check in checks:
            self.checks[check] = value

    def unset_checks(self, checks, value=False):
        """
        :param checks: List of checks names
        :type checks: list
        :param value: –
        :type value: –

        .. sealso: set_checks()
        """
        self.set_checks(checks, value)

    #--- PyScribus standard methods ----------------------------

    def toxml(self):
        if self.checks:
            xml = ET.Element("CheckProfile")
            xml.attrib["Name"] = self.name
            xml.attrib["autoCheck"] = bool_to_num(self.checks["auto"])

            for check in self.checks.keys():
                if check != "auto":
                    xml.attrib["check{}".format(check)] = bool_to_num(self.checks[check])

            for ignore in self.ignores.keys():
                xml.attrib["ignore{}".format(ignore)] = bool_to_num(self.ignores[ignore])

            for res in self.resolution.keys():
                xml.attrib["{}Resolution".format(res)] = self.resolution[res].toxmlstr()

            return xml
        else:
            return False

    def fromxml(self, xml):
        name = xml.get("Name")

        if name is not None:
            self.name = name

        autocheck = xml.get("autoCheck")

        if autocheck is not None:
            self.checks["auto"] = num_to_bool(autocheck)

        for check in self.checks.keys():
            value = xml.get("check{}".format(check))

            if value is not None:
                self.checks[check] = num_to_bool(value)

        for ignore in self.ignores.keys():
            value = xml.get("ignore{}".format(ignore))

            if value is not None:
                self.ignores[ignore] = num_to_bool(value)

        for res in self.resolution.keys():
            value = xml.get("{}Resolution".format(res))

            if value is not None:
                self.resolution[res].value = int(value)

        return True

    def fromdefault(self, name):
        """
        """

        if name in self.pyscribus_defaults:
            self.name = name

            if name in [
                    "PDF 1.3", "PDF 1.4", "PDF 1.5", "PDF/X-1a", "PDF/X-3",
                    "PDF/X-4", "PostScript"]:

                self.ignores = {"Errors": False, "OffLayers": False}
                self.resolution = {
                    "min": dimensions.Dim(144, "dpi", True),
                    "max": dimensions.Dim(2400, "dpi", True)
                }

            if name == "PDF 1.3":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "Resolution", "Transparency", "RasterPDF", "ForGIF",
                        "FontNotEmbedded", "FontIsOpenType",
                        "AppliedMasterDifferentSide", "EmptyTextFrames"
                    ]
                )

                self.unset_checks(
                    [
                        "Annotations", "PartFilledImageFrames", "NotCMYKOrSpot",
                        "DeviceColorsAndOutputIntent"
                    ]
                )

            if name == "PDF 1.4":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "RasterPDF", "ForGIF", "FontNotEmbedded", "FontIsOpenType",
                        "AppliedMasterDifferentSide", "EmptyTextFrames",
                        "Resolution"
                    ]
                )

                self.unset_checks(
                    [
                        "checkPartFilledImageFrames", "checkTransparency",
                        "checkAnnotations", "checkNotCMYKOrSpot",
                        "checkDeviceColorsAndOutputIntent"
                    ]
                )

            if name == "PDF 1.5":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "Resolution", "RasterPDF", "ForGIF", "FontNotEmbedded",
                        "FontIsOpenType", "AppliedMasterDifferentSide", "EmptyTextFrames"
                    ]
                )

                self.unset_checks(
                    [
                        "checkNotCMYKOrSpot", "checkDeviceColorsAndOutputIntent",
                        "checkTransparency", "checkAnnotations", "PartFilledImageFrames"
                    ]
                )

            if name == "PDF/X-1a":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "Resolution", "Transparency", "Annotations", "RasterPDF",
                        "ForGIF", "NotCMYKOrSpot", "FontNotEmbedded", "FontIsOpenType",
                        "AppliedMasterDifferentSide", "EmptyTextFrames"
                    ]
                )

                self.unset_checks(
                    [
                        "checkPartFilledImageFrames",
                        "checkDeviceColorsAndOutputIntent"
                    ]
                )

            if name == "PDF/X-3":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "Resolution", "Transparency", "Annotations", "RasterPDF",
                        "ForGIF", "DeviceColorsAndOutputIntent", "FontNotEmbedded",
                        "FontIsOpenType", "AppliedMasterDifferentSide", "EmptyTextFrames"
                    ]
                )

                self.unset_checks(
                    [
                        "checkPartFilledImageFrames", "checkNotCMYKOrSpot"
                    ]
                )

            if name == "PDF/X-4":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "Resolution", "Annotations", "RasterPDF", "ForGIF",
                        "DeviceColorsAndOutputIntent", "FontNotEmbedded",
                        "AppliedMasterDifferentSide", "EmptyTextFrames"
                    ]
                )

                self.unset_checks(
                    [
                        "checkPartFilledImageFrames", "checkTransparency",
                        "checkNotCMYKOrSpot", "checkFontIsOpenType"
                    ]
                )

            if name == "PostScript":
                self.set_checks(
                    [
                        "auto", "Glyphs", "Orphans", "Overflow", "Pictures",
                        "Resolution", "Transparency", "RasterPDF", "ForGIF",
                        "AppliedMasterDifferentSide", "EmptyTextFrames"
                    ]
                )

                self.unset_checks(
                    [
                        "checkPartFilledImageFrames", "checkAnnotations",
                        "checkNotCMYKOrSpot", "checkDeviceColorsAndOutputIntent",
                        "checkFontNotEmbedded", "checkFontIsOpenType"
                    ]
                )

        else:
            return False


class Layer(PyScribusElement):
    """
    Layer in SLA (LAYERS)

    :type default: bool
    :param default: Set default attributes for layer
    """

    blendmodes_to_xml = {
        "normal": "0", "darken": "1", "lighten": "2", "multiply": "3", "screen": "4",
        "overlay": "5", "hard-light": "6", "soft-light": "7", "substract": "8",
        "exclusion": "9", "color-dodge": "10", "color-burn": "11", "hue": "12",
        "saturation": "13", "color": "14", "luminosity": "15",
    }

    def __init__(self, default=False):
        super().__init__()

        if default:
            self.fromdefault()
        else:
            self.name = ""
            self.level = 0
            self.number = 0
            self.opacity = dimensions.Dim(1, "pcdecim")
            self.visible = True
            self.editable = True
            self.printable = True
            self.color = "#000000"
            self.wireframe = False
            self.blend = "normal"
            self.flow = False
            self.selectable = False

    def fromdefault(self):
        self.name = "Fond de page"
        self.level = 0
        self.number = 0
        self.visible = True
        self.editable = True
        self.printable = True
        self.color = "#000000"
        self.wireframe = False
        self.opacity = dimensions.Dim(1, "pcdecim")
        self.blend = "normal"
        self.flow = True
        self.selectable = False

    def fromxml(self, xml):
        number = xml.get("NUMMER")

        if number is not None:
            self.number = int(number)

            name = xml.get("NAME")
            edit = xml.get("EDIT")
            level = xml.get("LEVEL")
            color = xml.get("LAYERC")
            visible = xml.get("SICHTBAR")
            printable = xml.get("DRUCKEN")
            opacity = xml.get("TRANS")
            wireframe = xml.get("OUTL")
            # Blend mode of layer
            blend = xml.get("BLEND")
            # Habillage des cadres actif
            flow = xml.get("FLOW")
            # Objets du calque selectionnables même si le calque est non sélectionné
            selectable = xml.get("SELECT")

            if color is not None:
                self.color = color

            if name is not None:
                self.name = name

            if level is not None:
                self.level = int(level)

            if edit is not None:
                self.editable = num_to_bool(edit)

            if visible is not None:
                self.visible = num_to_bool(visible)

            if printable is not None:
                self.printable = num_to_bool(printable)

            if opacity is not None:
                self.opacity.value = float(opacity)

            if wireframe is not None:
                self.wireframe = num_to_bool(wireframe)

            if flow is not None:
                self.flow = num_to_bool(flow)

            if selectable is not None:
                self.selectable = num_to_bool(selectable)

            if blend is not None:

                for code,human in Layer.blendmodes_to_xml.items():

                    if code == blend:
                        self.blend = human
                        break

            return True

        else:
            return False

    def toxml(self):
        xml = ET.Element("LAYERS")

        xml.attrib["NUMMER"] = str(self.number)
        xml.attrib["LEVEL"] = str(self.level)
        xml.attrib["NAME"] = self.name

        for case in [
            ["SICHTBAR", self.visible], ["DRUCKEN", self.printable],
            ["EDIT", self.editable], ["SELECT", self.selectable],
            ["FLOW", self.flow]]:
            xml.attrib[case[0]] = bool_to_num(case[1])

        xml.attrib["TRANS"] = self.opacity.toxmlstr()
        xml.attrib["BLEND"] = Layer.blendmodes_to_xml[self.blend]
        xml.attrib["OUTL"] = bool_to_num(self.wireframe)
        xml.attrib["LAYERC"] = self.color

        return xml

# vim:set shiftwidth=4 softtabstop=4 spl=en:
