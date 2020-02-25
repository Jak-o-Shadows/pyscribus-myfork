#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Testing tables objects
"""

import pyscribus.sla as sla
import pyscribus.pageobjects as pageobjects

if __name__ == "__main__":
    # ---------------------------------------------------------------

    # Import the SLA file

    slafile = sla.SLA("tests/tables.sla", "1.5.5")

    # Gets all tables frames in the document
    tables = slafile.pageobjects("table")

    # ---------------------------------------------------------------

    print("Cells :")

    # Selects the last table frame in the document
    last = tables[-1]

    # Shows each cell information
    for c in last.cells:
        print(c.row, c.column, c.story.rawtext(), "|", c.box)

    # ---------------------------------------------------------------

    # Appends a column at the end and returns the new cells
    column_cells = last.append_column()

    # Appends a row at the end and returns the new cells
    row_cells = last.append_row()

    for case in zip(column_cells, ["D", "E", "F"]):
        case[0].story.append_paragraph(
           text=case[1]
        )

    for case in zip(row_cells, ["G", "H"]):
        case[0].story.append_paragraph(
           text=case[1]
        )

    # ---------------------------------------------------------------

    at_row_cells = last.append_row(position=1)

    # ---------------------------------------------------------------

    slafile.save("tests-outputs/tables.sla")

# vim:set shiftwidth=4 softtabstop=4:
