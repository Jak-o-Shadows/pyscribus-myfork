#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Testing stories PSM
"""

import pyscribus.stories as stories
import pyscribus.marks as marks

if __name__ == "__main__":
    print("--------------------------------------")

    a = stories.sequencefromhtml(
        "<em>So the <em>interview</em> did well.</em>.",
    )

    for i in a:
        print(i.__repr__())

    print("\nWith alternate emphasis :\n")

    b = stories.sequencefromhtml(
        "<em>So the <em>interview</em> did well.</em>.",
        alternate_emphasis=True

    )

    for i in b:
        print(i.__repr__())

    print("--------------------------------------")

    a = stories.sequencefromhtml(
        "Le <span style='font-variant: small-caps;'>xx</span><sup>e</sup> "
        "siècle est le siècle des <u>guerres mondiales</u>."
    )

    for i in a:
        print(i.__repr__())

    print("\nWith PSM :\n")

    b = stories.sequencefromhtml(
        "Le <sc>xx</sc><sup>e</sup> siècle est le siècle des "
        "<u>guerres mondiales</u>."
    )

    for i in b:
        print(i.__repr__())

    print("--------------------------------------")

    s = stories.Story()

    s.append_paragraph(text="Le chant du cygne est très beau.", style="Normal")
    s.append_paragraph(text="- Où as-tu <em>vu</em> ça ?", inherit_style=True)
    s.append_paragraph(text="- Je l’ai lu dans un livre.", ending=False)

    print("\n" + s.rawtext() + "\n")

    for i in s.sequence:
        print(i.__repr__())

    print("--------------------------------------")

    s = stories.Story()
    s.append_paragraphs(
        [
            {"text": "A title", "style": "Title1"},
            {"text": "Foreword", "style": "Foreword"},
            {
                "text": "First paragraph of content.",
                "style": "Normal"
            },
            {
                "text": "<em>Second</em> paragraph of content.",
                "inherit_style": True
            },
            {
                "text": "Third paragraph<note id='1'>A footnote text.</note>.",
                "inherit_style": True
            },
            {
                "text": "Fourth paragraph<span class='note' id='2'>A footnote text.</span>.",
                "inherit_style": True
            },
            {
                "text": "03/01/2020",
                "ending": False
            }
        ]
    )

    print("\n" + s.rawtext() + "\n")

    for i in s.sequence:
        print(i.__repr__())

    print("--------------------------------------")

# vim:set shiftwidth=4 softtabstop=4:
