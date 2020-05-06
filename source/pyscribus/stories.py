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
PyScribus classes for stories
"""

# Imports ===============================================================#

import lxml
import lxml.etree as ET

import pyscribus.exceptions as exceptions
import pyscribus.marks as marks
import pyscribus.notes as notes

from pyscribus.common.xml import *

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Classes ===============================================================#

class StoryEnding(PyScribusElement):
    """
    Ending marker in Scribus stories (trail)
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.alignment = None
        self.parent = None

    def toxml(self):
        xml = ET.Element("trail")

        if self.alignment is not None:
            xml.attrib["ALIGN"] = self.alignment

        if self.parent is not None:
            xml.attrib["PARENT"] = self.parent

        return xml

    def fromxml(self, xml):
        if xml.tag == "trail":

            if (align := xml.get("ALIGN")) is not None:
                # TODO use human values...
                self.alignment = align

            if (parent := xml.get("PARENT")) is not None:
                self.parent = parent

            return True

        return False


class StoryDefaultStyle(OrphanElement):
    """
    Default style marker in Scribus stories (DefaultStyle)
    """

    def __init__(self):
        OrphanElement.__init__(self, "DefaultStyle")


class StoryLineBreak(OrphanElement):
    """
    Line break marker in Scribus stories (breakline)
    """

    def __init__(self):
        OrphanElement.__init__(self, "breakline")


class NonBreakingHyphen(OrphanElement):
    """
    Non breaking hyphen in Scribus stories (nbhyphen)
    """

    def __init__(self):
        OrphanElement.__init__(self, "nbhyphen")


class NonBreakingSpace(OrphanElement):
    """
    Non breaking space in Scribus stories (nbspace)
    """

    def __init__(self):
        OrphanElement.__init__(self, "nbspace")


class StoryParagraphEnding(PyScribusElement):
    """
    End of paragraph marker in Scribus stories (para)

    :type parent: string
    :param parent: Name of the paragraph style
    :type doc_parent: pyscribus.document.Document
    :param parent: Parent Document instance

    :ivar string parent: Name of the paragraph style
    """

    def __init__(self, parent=False, doc_parent=False):
        super().__init__()

        self.parent = parent

        self.doc_parent = False

    def __repr__(self):
        return "PARAGEND|{}".format(self.parent)

    def fromxml(self, xml, check_style=True):
        if (parentpar := xml.get("PARENT")) is None:
            self.parent = False
        else:
            self.parent = parentpar

            if check_style and self.parent:

                if self.doc_parent:

                    checked = False

                    for para_style in self.doc_parent.styles["paragraph"]:
                        if para_style.name == self.parent:
                            checked = True
                            break

                    if not checked:
                        raise exceptions.UnknownStyleInStory(self.parent)

        return True

    def toxml(self):
        xml = ET.Element("para")

        if self.parent:
            xml.attrib["PARENT"] = self.parent

        return xml


class StoryFragment(PyScribusElement):
    """
    Text fragment (ITEXT) in Scribus stories.

    :type kwargs: dict
    :param kwargs: Quick setting (see kwargs table)

    :ivar string text: Text content
    :ivar dict font: Font details
    :ivar dict features: Font special formatting

    +----------------+---------------------------------+--------------+
    | Kwargs         | Setting                         | Type         |
    +================+=================================+==============+
    | text           | Fragment text                   | string       |
    +----------------+---------------------------------+--------------+
    | font           | Font name                       | string       |
    +----------------+---------------------------------+--------------+
    | fontsize       | Font size                       | float        |
    +----------------+---------------------------------+--------------+
    | fontcolor      | Font color name                 | string       |
    +----------------+---------------------------------+--------------+
    | fontopacity    | Font opacity                    | float        |
    |                |                                 | (percentage) |
    +----------------+---------------------------------+--------------+
    | default        | Equivalent to a fromdefault     | boolean or   |
    |                | call, value being True or the   | string       |
    |                | default name                    |              |
    +----------------+---------------------------------+--------------+
    | features       | Fragment features               | dict         |
    +----------------+---------------------------------+--------------+
    | inherit        | Font feature : inherit          | boolean      |
    +----------------+---------------------------------+--------------+
    | smallcaps      | Font feature : small caps       | boolean      |
    +----------------+---------------------------------+--------------+
    | allcaps        | Font feature : all caps         | boolean      |
    +----------------+---------------------------------+--------------+
    | superscript    | Font feature : superscript      | boolean      |
    +----------------+---------------------------------+--------------+
    | strike         | Font feature : striked          | boolean      |
    +----------------+---------------------------------+--------------+
    | subscript      | Font feature : subscript        | boolean      |
    +----------------+---------------------------------+--------------+
    | underline      | Font feature : underlined       | boolean      |
    +----------------+---------------------------------+--------------+
    | underlinewords | Font feature : underlined words | boolean      |
    +----------------+---------------------------------+--------------+

    :Example:

    .. code:: python

       frag = stories.StoryFragment(
           text="Lorem ipsum", fontsize=7, fontcolor="Grey"
       )

    """

    def __init__(self, **kwargs):
        super().__init__()

        self.text = ""

        # To not export to XML. This is defined by the following
        # StoryParagraphEnding in Story.sequence
        self.paragraph_style = False

        self.font = {
            "name": False,
            "size": False,
            "color": False,
            "opacity": False
        }

        # Features
        self.features = {
            "inherit": False,
            "smallcaps": False,
            "allcaps": False,
            "superscript": False,
            "strike": False,
            "subscript": False,
            "underline": False,
            "underlinewords": False,
        }

        if kwargs:
            self._quick_setup(kwargs)

    def _quick_setup(self, settings):
        """
        Method for defining story fragment settings from class
        instanciation kwargs.

        :type settings: dict
        :param settings: Kwargs dictionnary
        """

        if settings:
            PyScribusElement._quick_setup(self, settings)

            for setting_name, setting_value in settings.items():

                if setting_name == "text":
                    self.text = setting_value

                if setting_value == "features":
                    self.features = setting_value

                if setting_name == "fontsize":
                    self.font["size"] = setting_value

                if setting_name == "fontcolor":
                    self.font["color"] = setting_value

                if setting_name == "fontopacity":
                    self.font["opacity"] = setting_value

                if setting_name == "font":
                    self.font["name"] = setting_value

                if setting_name in self.features.keys():

                    if setting_value:
                        self.features[setting_name] = True
                    else:
                        self.features[setting_name] = False

    def fromdefault(self):
        self.text = ""

        self.paragraph_style = False

        self.font = {
            "name": False,
            "size": False,
            "color": False,
            "opacity": False
        }

        self.features = {
            "inherit": False,
            "smallcaps": False,
            "allcaps": False,
            "superscript": False,
            "strike": False,
            "subscript": False,
            "underline": False,
            "underlinewords": False,
        }

    def __iadd__(self, fragment):
        """
        += operator can be used to join another fragment text.

        The second term **inherits the features of the first**.
        """
        if isinstance(fragment, StoryFragment):
            self.text += fragment.text
            return self
        else:
            raise TypeError()

    def __repr__(self):
        def font_repr(f):
            if f:
                return f
            else:
                return ""

        def features_repr(f):
            return [k for k in f if f[k]]

        return "FRAGMENT|{}|{}|{}".format(
            font_repr(self.font["name"]),
            self.text,
            features_repr(self.features)
        )

    def __str__(self):
        return self.text

    def toxml(self):
        xml = ET.Element("ITEXT")

        have_features = len([f for f in self.features.values() if f])

        if have_features:
            features = []

            for f,v in self.features.items():
                if v:
                    features.append(f)

            features = " ".join(features)

            xml.attrib["FEATURES"] = features

        for case in zip(
                    ["name", "color", "opacity", "size"],
                    ["FONT", "FCOLOR", "FSHADE", "FONTSIZE"],
                    ):
            if self.font[case[0]]:
                xml.attrib[case[1]] = self.font[case[0]]

        xml.attrib["CH"] = self.text

        return xml

    def fromxml(self, xml):
        if (fragtext := xml.get("CH")) is not None:

            # NOTE Don't do any strip, rstrip to @CH, as it may
            # contains legitimate spaces
            self.text = fragtext

            if (features := xml.get("FEATURES")) is not None:
                self.set_features(features)

            for case in zip(
                        ["name", "color", "opacity", "size"],
                        ["FONT", "FCOLOR", "FSHADE", "FONTSIZE"],
                        ):

                if (att := xml.get(case[1])) is not None:
                    self.font[case[0]] = att

            # TODO Reste de l’implémentation, puis :

            return True
        else:
            return False

    def set_features(self, features):
        # TODO

        features = features.split()

        for feature in features:
            if feature in self.features.keys():
                self.features[feature] = True


class StoryVariable(PyScribusElement):
    """
    Variable in a Scribus story (var).

    :type name: string
    :param name: Name of the variable. Must be in StoryVariable.var_names.

    :ivar string name: Name of the variable
    """

    var_names = ["pgno", "pgco"]

    def __init__(self, name=""):
        super().__init__()

        if nam in StoryVariable.var_names or nam == "":
            self.name = name

    def toxml(self):
        """
        :rtype: lxml.etree._Element
        :returns: XML representation of story variable
        """

        element = ET.Element("var")

        element.attrib["name"] = self.name

        return element

    def fromxml(self, xml):
        """
        :rtype: boolean
        :returns: True if XML parsing succeed
        """

        if xml.tag == "var":

            if (nam := xml.get("name")) is None:
                return False
            else:
                if nam in StoryVariable.var_names:
                    self.name = nam

            return True

        else:
            return False


class PageNumberVariable(StoryVariable):
    """
    Page number variable in a Scribus story
    """

    def __init__(self):
        super().__init__("pgno")

class PageCountVariable(StoryVariable):
    """
    Count of total pages variable in a Scribus story
    """

    def __init__(self):
        super().__init__("pgco")

# Variables globales 2 ==================================================#

variable_classes = {
    "pgno": PageNumberVariable,
    "pgco": PageCountVariable,
}

# Parsing functions =====================================================#

def sequencefromhtml(
        html,
        font={
            "italic": "Arial Italic",
            "bold": "Arial Bold",
            "bold-italic": "Arial Bold Italic"},
        alternate_emphasis=False,
        sla_document=False):
    """
    :type html: string
    :param html: Paragraph text in PSM (PyScribus Story Markup)
    :type font: dict
    :param font: Fonts used for text emphasis
    :type alternate_emphasis: boolean
    :param alternate_emphasis: Nested emphasis returns to regular font.
    :type sla_document: pyscribus.document.Document
    :param sla_document: Instance of PyScribus Document where notes & marks will 
        be stored.
    :rtype: list
    :returns: List of pyscribus.stories.Story sequence elements
    """

    def tag_to_data(fragment, tag):
        """
        Modify fragment font and features according to tag value.
        """

        if tag in ["em", "i"]:
            fragment.font = font["italic"]

        if tag in ["b", "strong"]:
            fragment.font = font["bold"]

        if tag in ["sup"]:
            fragment.features["superscript"] = True

        if tag in ["sub"]:
            fragment.features["subscript"] = True

        if tag in ["u"]:
            fragment.features["underline"] = True

        if tag in ["sc"]:
            fragment.features["smallcaps"] = True

        return fragment

    def attrib_to_data(fragment, element):
        """
        Read @style attribute of element and modify fragment features
        accordingly.
        """

        if element.tag == "span":

            if "style" in element.attrib:
                css = [
                    r.strip()
                    for r
                    in element.attrib["style"].split(";")
                ]

                for rule in css:

                    # Little cleaning -> CSS property name and value
                    rule = rule.replace(": ",":").split(":")
                    name,value = rule[0],":".join(rule[1:])

                    if name == "font-variant":

                        if value == "small-caps":
                            fragment.features["smallcaps"] = True

                    if name == "text-transform":

                        if value == "uppercase":
                            fragment.features["allcaps"] = True

                    if name == "text-decoration":

                        if value == "underline":
                            fragment.features["underline"] = True

        return fragment

    def parse_note(element, sequence, sla_document):
        """
        Parse note XML data wether it comes from a <note> or a
        <span class="note"> element.
        """
        nid = element.get("id")

        if nid is None:
            raise ValueError(
                "<note> without @id."
            )
        else:
            # Mark of the note in the story ----------------------

            story_note = marks.StoryNoteMark(label=nid)
            story_note.fromdefault()

            # Note content in DOCUMENT ---------------------------

            # TODO FIXME Now that the mark is in the story,
            # we must add the note content into the DOCUMENT
            # <Notes>

            if sla_document:
                document_note = notes.Note()
                document_note.fromdefault()
                document_note.parent_mark = nid

                # TODO FIXME Handle note style
                # TODO FIXME Handle note text

                sla_document.notes.append(document_note)

            # Mark of the note in the DOCUMENT marks -------------

            if sla_document:
                document_mark = marks.DocumentMark()
                document_mark.fromdefault("note")
                document_mark.label = nid
                sla_document.marks.append(document_mark)

            # ----------------------------------------------------

            sequence.append(story_note)

        return sequence, sla_document

    def parse_element(element, sequence, font, previous, alternate_emphasis, sla_document):
        global variable_classes

        if element.tag in ["em", "i", "span", "b", "strong", "sup", "sub", "u", "sc"]:
            is_fragment = True

        if element.tag == "note":
            is_fragment = False

            sequence, sla_document = parse_note(element, sequence, sla_document)

        if element.tag in ["pgno", "pgco"]:
            is_fragment = False

            variable = Story.variable_classes[element.tag]()
            sequence.append(variable)

        if element.tag == "br":
            is_fragment = False
            sequence.append(StoryLineBreak())

        if element.tag == "span":

            if "class" in element.attrib:
                element_classes = [
                    cn.strip()
                    for cn in element.attrib["class"].strip().split()
                ]

                # Get the count of incompatible classes in span @class attribute
                # So <span class="pgno note"></span> will not work.
                main_class = len(
                    [
                        c
                        for c in ["pgno", "pgco", "note"]
                        if c in element_classes
                    ]
                )

                if main_class <= 1:

                    for element_class in element_classes:
                        # NOTE This iteration to check multiple classes in @class
                        # attribute, if a precision of a class is needed.

                        if element_class in ["pgno", "pgco"]:
                            is_fragment = False

                            variable = Story.variable_classes[element_class]()
                            sequence.append(variable)

                            break

                        if element_class == "note":
                            is_fragment = False

                            sequence, sla_document = parse_note(
                                element, sequence, sla_document
                            )

                            break
                else:
                    raise ValueError(
                        "Incompatible classes in span element @class : '{}'".format(
                            ",".join(element_classes)
                        )
                    )

        if is_fragment:
            fragment = StoryFragment(text=element.text)

            read_tag = True

            if alternate_emphasis:
                # If <em>lorem <em>ipsum</em> et dolor</em> must
                # produce an "ipsum" in regular style surrounded
                # by "lorem", "et dolor" both in italic.
                # Same thing for bold.

                if previous.tag in ["b", "strong", "i", "em"]:
                    if element.tag in ["b", "strong", "i", "em"]:
                        read_tag = False

            if read_tag:
                fragment = tag_to_data(fragment, element.tag)

            fragment = attrib_to_data(fragment, element)

            sequence.append(fragment)

        if len(element):

            for sub_element in element:

                sequence = parse_element(
                    sub_element,
                    sequence,
                    font,
                    element,
                    alternate_emphasis,
                    sla_document
                )

        if element.tail is not None:
            tail_fragment = StoryFragment(text=element.tail)
            tail_fragment = tag_to_data(tail_fragment, previous.tag)
            tail_fragment = attrib_to_data(tail_fragment, previous)

            sequence.append(tail_fragment)

        return sequence

    global variable_classes

    # Prepare parsing -----------------------------------------------

    # Encapsulate html in a <p> element if it doesn't exists, to
    # make lxml parsing work.

    if not html.startswith("<p>"):
        html = "<p>{}".format(html)

    if not html.endswith("</p>"):
        html = "{}</p>".format(html)

    parsed = ET.fromstring(html)

    # Parsing--------------------------------------------------------

    sequence = []

    if parsed.text is not None:
        sequence.append(StoryFragment(text=parsed.text))

    if len(parsed):

        for element in parsed:

            sequence = parse_element(
                element,
                sequence,
                font,
                parsed,
                alternate_emphasis,
                sla_document
            )

    if parsed.tail is not None:
        sequence.append(StoryFragment(text=parsed.tail))

    # ---------------------------------------------------------------

    return sequence

# Story class ===========================================================#

class Story(PyScribusElement):
    """
    Story in SLA (StoryText). A text buffer.

    :type sla_parent: pyscribus.sla.SLA
    :param sla_parent: Parent SLA instance.
    :type doc_parent: pyscribus.document.Document
    :param doc_parent: Parent Document instance.
    :type pgo_parent: pyscribus.pageobjects.PageObject
    :param pgo_parent: Parent page object instance.

    :ivar pyscribus.sla.SLA sla_parent: Parent SLA instance.
    :ivar pyscribus.document.Document doc_parent: Parent Document instance.
    :ivar list sequence: List of instances of StoryFragment,
        StoryParagraphEnding, StoryLineBreak, StoryDefaultStyle,
        NonBreakingHyphen, StoryVariable
    """

    def __init__(self, sla_parent=False, doc_parent=False, pgo_parent=False):
        super().__init__()

        self.sequence = []

        self.sla_parent = sla_parent
        self.doc_parent = doc_parent
        self.pgo_parent = pgo_parent

    def _without_ending(self):
        temp = []

        if self.sequence:
            if isinstance(self.sequence[-1], StoryEnding):
                temp = self.sequence[:-1]

        return temp

    def append_paragraph(self, **kwargs):
        """
        Append a paragraph at the end of the story.

        :type kwargs: dict
        :param kwargs: kwargs

        +-------------------+--------------+---------+--------------------------+
        | Kwargs key        | Kwargs value | Default |Usage                     |
        +===================+==============+=========+==========================+
        |text               | string       | False   | Paragraph text in PSM    |
        |                   |              |         | (PyScribus Story Markup) |
        +-------------------+--------------+---------+--------------------------+
        |ending             | boolean      | True    | Add a paragraph ending   |
        +-------------------+--------------+---------+--------------------------+
        |inherit_style      | boolean      | False   | Inherit paragraph style  |
        |                   |              |         | from last paragraph      |
        +-------------------+--------------+---------+--------------------------+
        |style              | string       | False   | Style of the paragraph.  |
        |                   |              |         | Overrides inherit_style. |
        +-------------------+--------------+---------+--------------------------+
        |alternate_emphasis | boolean      | False   | Nice emphasis, as nested |
        |                   |              |         | italic in italic becames |
        |                   |              |         | regular. Same for bold   |
        |                   |              |         | nested in bold.          |
        +-------------------+--------------+---------+--------------------------+

        As there is only one paragraph added by append_paragraph, the <p> element,
        enclosing the paragraph, can be omitted in text argument.

        :Example:

        .. code:: python

           story.append_paragraph(
               text="Le chant du cygne est très beau.", style="Normal"
           )
           story.append_paragraph(
               text="- Où as-tu <em>vu</em> ça ?", inherit_style=True
           )
           story.append_paragraph(
               text="<p>Et c'est ainsi qu'ils se quittèrent</p>",
               ending=False
           )

        """

        self._append_paragraph(kwargs)

        return True

    def append_paragraphs(self, paragraphs=[]):
        """
        Append multiple paragraphs at the end of the story.

        :type paragraphs: list
        :param paragraphs: List of Story.append_paragraph() kwargs dictionnaries.

        :Example:

        .. code:: python

           story.append_paragraphs(
              [
                  {"text": "A title", "style": "Title1"},
                  {"text": "Foreword", "style": "Foreword"},
                  {
                      "text": "First paragraph of content",
                      "style": "Normal"
                  },
                  {
                      "text": "Second paragraph of content",
                      "inherit_style": True
                  },
                  {"text": "03/01/2020", "ending": False}
              ]
           )

        .. seealso:: pyscribus.stories.Story.append_paragraph
        """

        if paragraphs:

            for paragraph in paragraphs:
                self._append_paragraph(paragraph)

            return True
        else:
            return False

    def _append_paragraph(self, kwargs):
        """
        Private method to append paragraph.

        Used by append_paragraph() and append_paragraphs()

        :type kwargs: dict
        :param paragraphs: kwargs of Story.append_paragraph()
        """

        # kwargs processing -------------------------------

        style,source,inherit_style = False,False,False
        alternate_emphasis = False

        ending = True

        font={
            "bold": "Arial Bold",
            "italic": "Arial Italic",
            "bold-italic": "Arial Bold Italic"
        }

        for param,value in kwargs.items():

            if param == "text":
                source = value

            if param == "ending":
                ending = bool(value)

            if param == "inherit_style":
                inherit_style = bool(value)

            if param == "style":
                style = value

            if param == "alternate_emphasis":
                alternate_emphasis = bool(value)

            if param == "font":

                if isinstance(value, dict):

                    for font_style in ["bold", "italic", "bold-italic"]:

                        if font_style not in value:

                            raise ValueError(
                                "Missing {} setting to font param".format(
                                    font_style
                                )
                            )

                    font = value

        # -------------------------------------------------

        sequence = sequencefromhtml(
            source,
            font=font,
            alternate_emphasis=alternate_emphasis,
            sla_document=self.doc_parent
        )

        if ending:
            para = StoryParagraphEnding()

            if style or inherit_style:
                ps = False

                # NOTE style overrides the inherited style

                if inherit_style:
                    # Get the last paragraph ending style

                    ps = [
                        e.parent
                        for e in self.sequence
                        if isinstance(e, StoryParagraphEnding)
                    ][-1]

                if style:
                    ps = style

                para.parent = ps

            sequence.append(para)

        temp = self._without_ending()
        self.sequence = temp + sequence
        self.end_contents()

    def toxml(self):
        """
        Return the story as XML element.

        :rtype: lxml._Element
        """

        xml = ET.Element("StoryText")

        for element in self.sequence:
            ex = element.toxml()
            xml.append(ex)

        return xml

    def fromxml(self, xml, check_style=True):
        """
        Parses XML of a SLA Story.

        :type xml: lxml._Element
        :param xml: SLA Story as lxml._Element
        :type check_style: bool
        :param check_style: Check if story paragraphs use known paragraph 
            styles of Story.doc_parent Document. True by default.

        .. note:: You might set check_style to False if you want to parse
            stories independantly of any given SLA & Document instances.

        :rtype: bool
        :returns: bool

        """

        global variable_classes

        if xml.tag == "StoryText":

            for element in xml:

                if element.tag == "DefaultStyle":
                    self.sequence.append(StoryDefaultStyle())

                if element.tag == "ITEXT":

                    frag = StoryFragment()
                    success = frag.fromxml(element)

                    if success:
                        self.sequence.append(frag)

                # End of a paragraph

                if element.tag == "para":
                    para = StoryParagraphEnding(self.doc_parent)
                    success = para.fromxml(element, check_style)

                    if success:

                        # NOTE @PARENT carries the style name of the preceding
                        # StoryFragment / <ITEXT> in the sequence

                        if para.parent:

                            # NOTE Empty lines in the story are just <para>
                            # following each others. So we only set the
                            # paragraph_style of the preceding fragment…
                            # if there *is* a fragment to begin with.

                            if isinstance(self.sequence[-1], StoryFragment):
                                self.sequence[-1].paragraph_style = para.parent

                        self.sequence.append(para)

                # Line break in a paragraph

                if element.tag == "breakline":
                    self.sequence.append(StoryLineBreak())

                # Non breaking hyphen

                if element.tag == "nbhyphen":
                    self.sequence.append(NonBreakingHyphen())

                # Non breaking space

                if element.tag == "nbspace":
                    self.sequence.append(NonBreakingSpace())

                # Mark

                if element.tag == "MARK":
                    # TODO Selon @type, un StoryNoteMark ou autre
                    pass

                # Variable

                if element.tag == "var":

                    var_name = element.get("name")

                    if var_name is not None:
                        var_instance = Story.variable_classes[var_name]()
                        self.sequence.append(var_instance)

                # Story end

                if element.tag == "trail":
                    story_ending = StoryEnding()
                    success = story_ending.fromxml(element)

                    if success:
                        self.sequence.append(story_ending)
                    break

            return True

        return False

    def fromdefault(self):
        """
        Set a default story
        """

        self.sequence = [StoryDefaultStyle(), StoryEnding()]

    def append(self, element):
        """
        Append a element to the Story sequence.

        .. warning:: Don't use append() to append a StoryEnding, use 
            end_contents() instead.

        :type element: StoryFragment, StoryParagraphEnding, StoryLineBreak, StoryDefaultStyle
        :param element: Element to add to the story sequence
        :rtype: bool
        :returns: bool

        .. seealso:: pyscribus.stories.end_contents
        """

        temp = self._without_ending()
        self.sequence = temp + [element]
        self.end_contents()

        return True

    def end_contents(self, no_trailing_paragraph=False):
        """
        Ends the story's content by making sure that the story sequence
        is valid.

        .. note:: It is better to use this method than appending a
            :class:`StoryEnding` instance directly into the story sequence.

        :type no_trailing_paragraph: bool
        :param no_trailing_paragraph: Remove last paragraph ending
        """
        story_ending = None

        if isinstance(self.sequence[-1], StoryEnding):
            story_ending = self.sequence.pop(-1)

        if no_trailing_paragraph:
            if isinstance(self.sequence[-1], StoryParagraphEnding):
                self.sequence.pop(-1)

        if story_ending is None:
            self.sequence.append(StoryEnding())
        else:
            self.sequence.append(story_ending)

    def init_contents(self):
        self.sequence = [StoryDefaultStyle()]

    def bypars(self):
        """
        Return a list of list of Story.sequence elements organized as human
        paragraphs.

        :returns: list of lists
        :rtype: ilst
        """

        pars = [] # List of paragraphs
        tmp = [] # Temporary list of paragraph elements

        for element in self.sequence:

            # End of the story -> last paragraph is added to the list

            if isinstance(element, StoryEnding):
                if tmp:
                    pars.append(tmp)
                    break

            # End of a paragraph ------------------------------------

            if isinstance(element, StoryParagraphEnding):

                if tmp:
                    tmp.append(element)
                    pars.append(tmp)
                    tmp = []

            # Paragraph content -------------------------------------

            for class_test in [StoryFragment, StoryDefaultStyle,
                    NonBreakingSpace, NonBreakingHyphen, StoryVariable]:

                if isinstance(element, class_test):
                    tmp.append(element)
                    break

        return pars

    def rawtext(self):
        """
        Returns a text string equivalent to *what Scribus story editor
        saves* as txt file.

        :rtype: string
        """
        text = ""

        for par in self.bypars():

            for element in par:

                # NOTE Text formatting is not saved
                if isinstance(element, StoryFragment):
                    text += element.text

                if isinstance(element, NonBreakingSpace):
                    text += " "

                # NOTE Line breaks are exported by Scribus... as spaces
                if isinstance(element, StoryLineBreak):
                    text += " "

                if isinstance(element, StoryParagraphEnding):
                    text += "\n"

        return text

    def templatable(self):
        """
        Return elements of Story sequence that are available for templating.

        :rtype: list
        :returns: List of pyscribus.stories.StoryFragment
        """

        contents = []

        pattern = self.sla_parent.templating["intext-pattern"]

        for element in self.sequence:

            if isinstance(element, StoryFragment):

                if pattern.search(element.text):
                    contents.append(element)

        return contents

    def feed_templatable(self, datas={}):
        """
        """

        elements = self.templatable()

        if elements:
            modified = []

            for element in elements:

                if element.text in datas:
                    element.text = element.text.replace(
                        element.text,
                        datas[element.text]
                    )

                    modified.append(element)

            return modified

        return False

# vim:set shiftwidth=4 softtabstop=4 spl=en:
