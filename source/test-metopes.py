#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Transforme une unité éditoriale Métopes en story Scribus.
"""

# Imports ===============================================================#

import os

import lxml
import lxml.etree as ET

import pyscribus.sla as sla
import pyscribus.stories as stories
import pyscribus.marks as marks
import pyscribus.styles as pstyles

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

# Polices employées.

FONT = "Linux Libertine"
BOLD_FONT = FONT + " Bold"
ITALIC_FONT = FONT + " Italic"
BOLD_ITAL_FONT = FONT + "Bold Italic"

# Classes ===============================================================#

class MetopesUE:
    """
    """

    def __init__(self, filepath, fonts={"normal": "Arial"}):
        self.filepath = filepath

        self.parts = {
            "body": None, "front": None, "back": None
        }

        self.fonts = fonts

        if os.path.exists(os.path.realpath(filepath)):
            self.parse()

    def parse(self):

        def get_contents(xml, content_section):
            xp = '{http://www.tei-c.org/ns/1.0}text/'
            xp += '{http://www.tei-c.org/ns/1.0}' + content_section

            is_section = xml.findall(xp)

            if len(is_section):
                return is_section[0]
            else:
                return []

        xml = ET.parse(self.filepath).getroot()

        body = get_contents(xml, "body")
        front = get_contents(xml, "front")
        back = get_contents(xml, "back")

        if len(front):
            front_story = stories.Story()
            front_story.init_contents()

            front_story.end_contents(no_trailing_paragraph=True)

        if len(back):
            back_story = stories.Story()
            back_story.init_contents()

            back_story.end_contents(no_trailing_paragraph=True)

        if len(body):
            self.parts["body"] = stories.Story()
            self.parts["body"].init_contents()

            body_frags = []
            body_notes = []

            for main in body:
                if main.tag == teitag("div"):
                    div_frags, body_notes = analyse_div(main, body_notes)
                    body_frags += div_frags

            for i in body_frags:
                self.parts["body"].sequence.append(i)

            self.parts["body"].end_contents(no_trailing_paragraph=True)

    def save(self, filepath):
        text = str(
            ET.tostring(
                self.parts["body"].toxml(),
                encoding="unicode",
                pretty_print=True
            )
        )

        with open(filepath, "w", encoding="utf8") as to:
            to.write(text)

# Fonctions =============================================================#

def teitag(tag):
    return "{http://www.tei-c.org/ns/1.0}" + tag

def analyse_hi(xml):
    global BOLD_FONT
    global ITALIC_FONT
    global BOLD_ITAL_FONT

    frags = []

    first_frag = stories.StoryFragment()

    first_is_italic = False
    first_is_bold = False

    if "rend" in xml.attrib:
        rend = xml.attrib["rend"]

        if "italic" in rend or rend == "italic":
            first_frag.font = ITALIC_FONT
        elif "small-caps" in rend or rend == "small-caps":
            first_frag.features["smallcaps"] = True
        elif "line-through" in rend or rend == "line-through":
            first_frag.features["strike"] = True
        elif "underline" in rend or rend == "underline":
            first_frag.features["underline"] = True
        elif "capitale" in rend or rend == "capitale":
            first_frag.features["allcaps"] = True
        elif "bold" in rend or rend == "bold":
            first_frag.font = BOLD_FONT
        elif "sup" in rend or rend == "sup":
            first_frag.features["superscript"] = True
        else:
            print("rend:", rend)

    first_frag.text = xml.text
    frags.append(first_frag)

    if len(xml):
        for element in xml:
            if element.tag == teitag("hi"):
                sub_hi = analyse_hi(element)
                frags += sub_hi

    if xml.tail:
        frags.append(
            stories.StoryFragment(text=xml.tail)
        )

    return frags

def analyse_p(xml, notes, check_notes=True, check_hi=True, check_links=True):
    p_frags = []

    if xml.text is not None:
        frag_text = stories.StoryFragment(text=xml.text)
        p_frags.append(frag_text)

    if xml.tail is not None:
        frag_tail = stories.StoryFragment(text=xml.tail)
        p_frags.append(frag_tail)

    for inpara in xml:

        if inpara.tag == teitag("note"):
            if check_notes:
                p_frags, notes = analyse_note(p_frags, inpara, notes)
        elif inpara.tag == teitag("hi"):
            if check_hi:
                hi_frags = analyse_hi(inpara)
                p_frags += hi_frags
                continue
        elif inpara.tag == teitag("ref"):
            if check_links:
                lf = stories.StoryFragment(text=inpara.text)
                lf.features["underline"] = True
                p_frags.append(lf)
        else:
            print("Inconnu dans p", inpara.tag)

        if inpara.text is not None:
            third_frag_text = stories.StoryFragment(text=inpara.text)
            p_frags.append(third_frag_text)

        if inpara.tail is not None:
            third_frag_tail = stories.StoryFragment(text=inpara.tail)
            p_frags.append(third_frag_tail)

    style = xml.get("style")
    p_end = stories.StoryParagraphEnding()

    if style is not None:
        p_end.parent = style

    p_frags.append(p_end)

    return p_frags, notes

def analyse_quote(xml, notes):
    return analyse_p(xml, notes)

def analyse_list_item(xml, notes):
    li_frags = []

    if xml.text is not None:
        frag_text = stories.StoryFragment(text=xml.text)
        li_frags.append(frag_text)

    if xml.tail is not None:
        frag_tail = stories.StoryFragment(text=xml.tail)
        li_frags.append(frag_tail)

    for inpara in xml:

        if inpara.tag == teitag("note"):
            if check_notes:
                li_frags, notes = analyse_note(li_frags, inpara, notes)
        elif inpara.tag == teitag("hi"):
            if check_hi:
                hi_frags = analyse_hi(inpara)
                li_frags += hi_frags
                continue
        elif inpara.tag == teitag("ref"):
            if check_links:
                lf = stories.StoryFragment(text=inpara.text)
                lf.features["underline"] = True
                li_frags.append(lf)
        elif inpara.tag == teitag("list"):
            sublist_frags, notes = analyse_list(inpara, notes)
            li_frags += sublist_frags
        else:
            print("Inconnu dans p", inpara.tag)

        if inpara.text is not None:
            third_frag_text = stories.StoryFragment(text=inpara.text)
            li_frags.append(third_frag_text)

        if inpara.tail is not None:
            third_frag_tail = stories.StoryFragment(text=inpara.tail)
            li_frags.append(third_frag_tail)

    style = xml.get("style")
    li_end = stories.StoryParagraphEnding()

    if style is not None:
        li_end.parent = style

    li_frags.append(li_end)

    return li_frags, notes

def analyse_list(xml, notes):
    list_frags = []

    ltype = xml.get("type")

    for elem in xml:
        if elem.tag == teitag("item"):
            item_frags, notes = analyse_list_item(elem, notes)
            list_frags += item_frags

    return list_frags, notes

def analyse_note(frags, xml, notes):
    # Faire une marque

    note_mark = marks.StoryNoteMark()
    note_mark.fromdefault()
    frags.append(note_mark)

    note_frags = []

    for note_para in xml:
        if note_para.tag == teitag("p"):
            note_para_frags,_ = analyse_p(
                note_para,
                notes,
                check_notes=False
            )

            note_frags += note_para_frags

    notes.append(
        {
            "n": xml.attrib["n"],
            "content": note_frags
        }
    )

    return frags, notes

def analyse_head(xml, notes, check_notes=True, check_hi=True):
    head_frags = []

    if xml.text is not None:
        frag_text = stories.StoryFragment(text=xml.text)
        head_frags.append(frag_text)

    if xml.tail is not None:
        frag_tail = stories.StoryFragment(text=xml.tail)
        head_frags.append(frag_tail)

    for inhead in xml:
        if inpara.tag == teitag("hi"):
            if check_hi:
                hi_frags = analyse_hi(inhead)
                head_frags += hi_frags
                continue

        if inpara.tag == teitag("note"):
            if check_notes:
                head_frags, notes = analyse_note(head_frags, inpara, notes)

    style = xml.get("style")
    head_end = stories.StoryParagraphEnding()

    if style is not None:
        head_end.parent = style

    head_frags.append(head_end)

    return head_frags, notes

def analyse_div(xml, notes):
    div_frags = []

    print("-- div -----------------------------------------")

    for element in xml:

        found = False

        for case in [
                ["quote", analyse_quote], ["list", analyse_list],
                ["p", analyse_p], ["head", analyse_head],
                ["div", analyse_div]]:

            if element.tag == teitag(case[0]):
                case_frags, notes = case[1](element, notes)
                div_frags += case_frags
                found = True
                break

        if not found:
            print(element.tag)

    print("-- div (end) -----------------------------------")

    return div_frags, notes

# Programme =============================================================#

if __name__ == "__main__":
    ue = MetopesUE(
        "tests/metopes-test.xml",
        {
            "normal": "Linux Libertine",
            "bold": "Linux Libertine Bold",
            "italic": "Linux Libertine Italic",
            "bold-italic": "Linux Libertine Bold Italic",
        }
    )
    ue.save("tests-outputs/metopes-story.xml")

# vim:set shiftwidth=4 softtabstop=4:
