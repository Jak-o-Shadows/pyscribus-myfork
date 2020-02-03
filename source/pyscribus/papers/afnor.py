#!/usr/bin/python3
# -*- coding:Utf-8 -*-

# PyScribus, python library for Scribus SLA
# Copyright (C) 2020 Étienne Nadji
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
AFNOR (French Standardization Association) certified paper sizes.

"Old" [french] paper sizes.

Provides :

Cloche, Pot / Écolier, Tellière, Couronne écriture, Couronne édition,
Roberto, Écu, Coquille, Carré, Cavalier, Demi-raisin, Raisin,
Double raisin, Jésus, Soleil, Colombier affiche, Colombier commercial,
Petit Aigle, Grand Aigle, Grand Monde, Univers

For more common and international paper sizes, see iso216paper module.
"""

# Imports ===============================================================#

from pyscribus.common.math import FloatEnum, PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

class Cloche(FloatEnum):
    WIDTH = 300 / PICA_TO_MM
    HEIGHT = 400 / PICA_TO_MM

class Pot(FloatEnum):
    """
    Pot paper size. Same as Ecolier.
    """

    WIDTH = 310 / PICA_TO_MM
    HEIGHT = 400 / PICA_TO_MM

class Ecolier(FloatEnum):
    """
    Ecolier paper size. Same as Pot.
    """

    WIDTH = 310 / PICA_TO_MM
    HEIGHT = 400 / PICA_TO_MM

class Telliere(FloatEnum):
    WIDTH = 340 / PICA_TO_MM
    HEIGHT = 440 / PICA_TO_MM

class CouronneEcriture(FloatEnum):
    WIDTH = 360 / PICA_TO_MM
    HEIGHT = 460 / PICA_TO_MM

class CouronneEdition(FloatEnum):
    WIDTH = 370 / PICA_TO_MM
    HEIGHT = 470 / PICA_TO_MM

class Roberto(FloatEnum):
    WIDTH = 390 / PICA_TO_MM
    HEIGHT = 500 / PICA_TO_MM

class Ecu(FloatEnum):
    WIDTH = 400 / PICA_TO_MM
    HEIGHT = 520 / PICA_TO_MM

class Coquille(FloatEnum):
    WIDTH = 440 / PICA_TO_MM
    HEIGHT = 560 / PICA_TO_MM

class Carre(FloatEnum):
    WIDTH = 450 / PICA_TO_MM
    HEIGHT = 560 / PICA_TO_MM

class Cavalier(FloatEnum):
    WIDTH = 460 / PICA_TO_MM
    HEIGHT = 620 / PICA_TO_MM

class Raisin(FloatEnum):
    WIDTH = 500 / PICA_TO_MM
    HEIGHT = 650 / PICA_TO_MM

class DemiRaisin(FloatEnum):
    WIDTH = 325 / PICA_TO_MM
    HEIGHT = 500 / PICA_TO_MM

class DoubleRaisin(FloatEnum):
    WIDTH = 650 / PICA_TO_MM
    HEIGHT = 1000 / PICA_TO_MM

class Jesus(FloatEnum):
    WIDTH = 560 / PICA_TO_MM
    HEIGHT = 720 / PICA_TO_MM

class PetitJesus(FloatEnum):
    WIDTH = 550 / PICA_TO_MM
    HEIGHT = 700 / PICA_TO_MM

class GrandJesus(FloatEnum):
    WIDTH = 560 / PICA_TO_MM
    HEIGHT = 760 / PICA_TO_MM

class Soleil(FloatEnum):
    WIDTH = 600 / PICA_TO_MM
    HEIGHT = 800 / PICA_TO_MM

class ColombierAffiche(FloatEnum):
    WIDTH = 600 / PICA_TO_MM
    HEIGHT = 800 / PICA_TO_MM

class ColombierCommercial(FloatEnum):
    WIDTH = 630 / PICA_TO_MM
    HEIGHT = 900 / PICA_TO_MM

class PetitAigle(FloatEnum):
    WIDTH = 700 / PICA_TO_MM
    HEIGHT = 940 / PICA_TO_MM

class GrandAigle(FloatEnum):
    WIDTH = 750 / PICA_TO_MM
    HEIGHT = 1060 / PICA_TO_MM

class GrandMonde(FloatEnum):
    WIDTH = 900 / PICA_TO_MM
    HEIGHT = 1260 / PICA_TO_MM

class Univers(FloatEnum):
    WIDTH = 1000 / PICA_TO_MM
    HEIGHT = 1300 / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
