#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import lxml
import lxml.etree as ET

import pyscribus.sla as sla
import pyscribus.stories as pstories
import pyscribus.styles as pstyles
import pyscribus.pageobjects as pobjects
import pyscribus.dimensions as dimensions

from pyscribus.common.math import mm
from pyscribus.papers.iso216 import A4

if __name__ == "__main__":
    slafile = sla.SLA(version="1.5.5")
    slafile.fromdefault()

    # --- ONIX file --------------------------------------------

    onix = ET.parse("tests/onix_3_imprimerie.xml").getroot()

    publishers = onix.findall("Product/PublishingDetail/Publisher/PublisherName")
    publishers = ", ".join([i.text for i in publishers])

    isbns = []
    pub_ids = onix.findall("Product/ProductIdentifier")

    for pub_id in pub_ids:
        ptype = False
        pvalue = False

        for child in pub_id:

            if child.tag == "ProductIDType":
                ptype = child.text

            if child.tag == "IDValue":
                pvalue = child.text

        if ptype and pvalue:

            if ptype == "03":
                isbns.append(pvalue)

    titles = []
    pub_titles = onix.findall("Product/DescriptiveDetail/TitleDetail")

    for title in pub_titles:

        prefix = ""
        content = ""
        level = 1

        for element in title:

            if element.tag == "TitleElement":

                for sub in element:

                    if sub.tag == "TitleElementLevel":
                        level = int(sub.text.strip())

                    if sub.tag == "TitlePrefix":
                        prefix = sub.text.strip()

                    if sub.tag == "TitleWithoutPrefix":
                        content = sub.text.strip()

                        if "textcase" in sub.attrib:

                            if sub.attrib["textcase"] == "01":
                                content = content[0].lower() + content[1:]

            if content:

                if prefix:
                    titles.append(
                        {
                            "text": "{}{}".format(prefix, content),
                            "level": level
                        }
                    )
                else:
                    titles.append(
                        {
                            "text": content,
                            "level": level
                        }
                    )

    summary, toc = False, False
    record = False

    summaries = onix.findall("Product/CollateralDetail/TextContent")

    for summ in summaries:
        text = False

        for element in summ:

            if element.tag == "TextType":
                record = int(element.text.strip())

            if element.tag == "Text":
                text = element.text

        if record and text:

            if record == 3:
                summary = text

            if record == 4:
                text = text.replace("&#60;", "<")
                text = text.replace("&#62;", ">")

                text = text.replace("\t", "")
                text = text.replace("\r", "")
                text = text.replace("\n", "")

                for i in range(2):
                    text = text.replace("  ", " ")

                text = text.split("<br />")
                text = [s.strip() for s in text if s.strip()]
                text = "<br />".join(text)

                toc = text

    collection = []
    collections = onix.findall("Product/DescriptiveDetail/Collection/TitleDetail")

    for coll in collections:
        coll_name = False

        for element in coll:

            if element.tag == "TitleElement":

                for sub in element:

                    if sub.tag == "TitleText":
                        coll_name = sub.text.strip()

        if coll_name:
            collection.append(coll_name)

    price = []
    prices = onix.findall("Product/ProductSupply/SupplyDetail/Price")

    for pr in prices:
        amount = False
        currency = False

        for element in pr:

            if element.tag == "PriceAmount":
                amount = float(element.text.strip())

            if element.tag == "CurrencyCode":
                if element.text.strip() == "EUR":
                    currency = "euro"

        if amount and currency:
            price.append({"amount": amount, "currency": currency})

    # --- Styles -----------------------------------------------

    document = slafile.documents[0]

    # As all defined styles will inherit Scribus default paragraph style,
    # we set its leading mode to "automatic".
    document.styles["paragraph"][0].leading["mode"] = "automatic"

    # Defining paragraph styles, with quick settings

    title_style = pstyles.ParagraphStyle(
        document,
        name="Title", fontsize=18, alignment="center", spaceafter=10,
    )

    title_h2 = pstyles.ParagraphStyle(
        document,
        name="H2", fontsize=14, spacebefore=5, spaceafter=10,
    )

    normal_style = pstyles.ParagraphStyle(
        document,
        name="Normal", fontsize=12, alignment="left",
    )

    summary_style = pstyles.ParagraphStyle(
        document,
        name="Summary", font="Arial Italic", fontsize=12,
        alignment="justify-left",
    )

    detail_style = pstyles.ParagraphStyle(
        document,
        name="Detail", fontsize=10,
    )

    # We add the styles via the general SLA.append() method

    for s in [title_style, title_h2, normal_style, summary_style, detail_style]:
        slafile.append(s)

    # --- Text frame -------------------------------------------

    margins = mm(14.111 * 2)

    text_frame = pobjects.TextObject(
        default=True,
        posx=140, posy=60,
        width=float(A4.WIDTH) - margins,
        height=float(A4.HEIGHT) - margins,
    )
    text_frame.object_id = "12868"

    text_frame.stories[0].append_paragraphs(
        [
            {"style":"Title", "text": titles[0]["text"]},
            {"style":"Summary", "text": summary},
            {"style":"H2", "text": "Sommaire"},
            {"style":"Normal", "text": toc},
            {"style":"H2", "text": "Détails"},
            {"style":"Detail", "text": "; ".join(collection)},
            {"style":"Detail", "text": "{} €".format(price[0]["amount"])},
            {"style":"Detail", "text": isbns[0]}
        ]
    )

    # ----------------------------------------------------------

    slafile.append(text_frame)

    slafile.save("tests-outputs/test-onix.sla")

# vim:set shiftwidth=4 softtabstop=4:
