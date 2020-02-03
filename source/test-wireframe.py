#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Draw a wireframe representation of a SLA file into "test_wireframe.png".
"""

import pyscribus.sla as sla
import pyscribus.extra.wireframe as wire

if __name__ == "__main__":
    slafile = sla.SLA("tests/images.sla", "1.5.5")

    wireframe = wire.Wireframe()
    wireframe.from_sla(slafile)

    wireframe.draw(
        output="tests-outputs/test_wireframe.png",
        stylesheet=True,
        margins=[10, 10]
    )

# vim:set shiftwidth=4 softtabstop=4:
