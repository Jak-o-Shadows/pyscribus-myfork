#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Test de création de SLA par défaut.
"""

import pyscribus.sla as sla

if __name__ == "__main__":
    testfile = sla.SLA(version="1.5.5")
    testfile.fromdefault()
    testfile.save("tests-outputs/test-fromdefault.sla")

# vim:set shiftwidth=4 softtabstop=4:
