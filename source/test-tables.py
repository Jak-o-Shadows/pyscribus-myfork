#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Testing tables objects
"""

import pyscribus.sla as sla
import pyscribus.pageobjects as pageobjects

if __name__ == "__main__":
    slafile = sla.SLA("tests/tables.sla", "1.5.5")

    tables = slafile.pageobjects("table")

    print("Cells :")

    last = tables[-1]

    for c in last.cells:
        print(c.row, c.column, c.story.rawtext(), "|", c.box)

    last.append_column()

    slafile.save("tests-outputs/tables.sla")

# vim:set shiftwidth=4 softtabstop=4:
