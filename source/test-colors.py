#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Tests for gradients and colors.
"""

import pyscribus.colors as colors
import pyscribus.dimensions as dimensions

if __name__ == "__main__":

    # Two identical gradient color stops

    cstop1 = colors.GradientColorStop(
        color="Black", shade=100, position=0, opacity=1
    )

    cstop2 = colors.GradientColorStop(
        color="Black", shade=100, position=0, opacity=1
    )

    print("Same color stops ?", cstop1 == cstop2)

    # Gradient

    gradient = colors.Gradient()
    gradient.name = "Test gradient"

    # Color stops with same values are not added

    gradient.append_stop(cstop1)
    gradient.append_stop(cstop2)
    print(gradient.stops)

    # We set cstop2 color to White so cstop1 and cstop2 are not the same
    # color stops anymore

    cstop2.color = "White"

    gradient.append_stop(cstop2)
    print(gradient.stops)

# vim:set shiftwidth=4 softtabstop=4:
