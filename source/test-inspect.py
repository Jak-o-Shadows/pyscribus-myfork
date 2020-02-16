#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
"""

import pyscribus.sla as sla

if __name__ == "__main__":
    slafile = sla.SLA("tests/images.sla")

    print(slafile.pageobjects("image"))

# vim:set shiftwidth=4 softtabstop=4:
