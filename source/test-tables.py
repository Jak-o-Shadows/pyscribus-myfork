#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Testing tables objects
"""

import pyscribus.sla as sla
import pyscribus.pageobjects as pageobjects

if __name__ == "__main__":
    sla = sla.SLA("tests/tables.sla", "1.5.5")

    for po in sla.documents[0].page_objects:
        if isinstance(po, pageobjects.TableObject):
            print(po)

            print("Borders :")
            print(po.borders)

            print("Cells :")
            for c in po.cells:
                print(c.row, c.column, c.story.rawtext())

# vim:set shiftwidth=4 softtabstop=4:
