#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Loads and immediatly exports to another file to check differences
between Scribus and PyScribus SLAs.
"""

import pyscribus.sla as sla

if __name__ == "__main__":
    slafile = sla.SLA("tests/images.sla", "1.5.5")
    slafile.save("tests-outputs/test-load-export.sla")

# vim:set shiftwidth=4 softtabstop=4:
