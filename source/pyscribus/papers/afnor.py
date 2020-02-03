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

from pyscribus.dimensions import PICA_TO_MM

# Variables globales ====================================================#

__author__ = "Etienne Nadji <etnadji@eml.cc>"

CLOCHE_WIDTH = 300 / PICA_TO_MM
CLOCHE_HEIGHT = 400 / PICA_TO_MM

POT_WIDTH = 310 / PICA_TO_MM
POT_HEIGHT = 400 / PICA_TO_MM

ECOLIER_WIDTH = POT_WIDTH
ECOLIER_HEIGHT = POT_HEIGHT

TELLIERE_WIDTH = 340 / PICA_TO_MM
TELLIERE_HEIGHT = 440 / PICA_TO_MM

COURONNE_ECRITURE_WIDTH = 360 / PICA_TO_MM
COURONNE_ECRITURE_HEIGHT = 460 / PICA_TO_MM

COURONNE_EDITION_WIDTH = 370 / PICA_TO_MM
COURONNE_EDITION_HEIGHT = 470 / PICA_TO_MM

ROBERTO_WIDTH = 390 / PICA_TO_MM
ROBERTO_HEIGHT = 500 / PICA_TO_MM

ECU_WIDTH = 400 / PICA_TO_MM
ECU_HEIGHT = 520 / PICA_TO_MM

COQUILLE_WIDTH = 440 / PICA_TO_MM
COQUILLE_HEIGHT = 560 / PICA_TO_MM

CARRE_WIDTH = 450 / PICA_TO_MM
CARRE_HEIGHT = 560 / PICA_TO_MM

CAVALIER_WIDTH = 460 / PICA_TO_MM
CAVALIER_HEIGHT = 620 / PICA_TO_MM

RAISIN_WIDTH = 500 / PICA_TO_MM
RAISIN_HEIGHT = 650 / PICA_TO_MM

DEMI_RAISIN_WIDTH = 325 / PICA_TO_MM
DEMI_RAISIN_HEIGHT = 500 / PICA_TO_MM

DOUBLE_RAISIN_WIDTH = 650 / PICA_TO_MM
DOUBLE_RAISIN_HEIGHT = 1000 / PICA_TO_MM

JESUS_WIDTH = 560 / PICA_TO_MM
JESUS_HEIGHT = 760 / PICA_TO_MM

# jesus-petit
# 1559.0551181102364
# 1984.2519685039372

# jesus-grand
# 1587.4015748031497
# 2154.3307086614177

SOLEIL_WIDTH = 600 / PICA_TO_MM
SOLEIL_HEIGHT = 800 / PICA_TO_MM

COLOMBIER_AFFICHE_WIDTH = 600 / PICA_TO_MM
COLOMBIER_AFFICHE_HEIGHT = 800 / PICA_TO_MM

COLOMBIER_COMMERCIAL_WIDTH = 630 / PICA_TO_MM
COLOMBIER_COMMERCIAL_HEIGHT = 900 / PICA_TO_MM

PETIT_AIGLE_WIDTH = 700 / PICA_TO_MM
PETIT_AIGLE_HEIGHT = 940 / PICA_TO_MM

# Grand Aigle
# 750 × 1067
# ou 750 × 1050
# ou parfois 750 × 1108

# aigle-grand-1
# 2125.984251968504
# 3004.724409448819

# aigle-grand-2
# 2125.984251968504
# 2976.377952755906

# aigle-grand-3
# 2125.984251968504
# 3118.110236220473

GRAND_MONDE_WIDTH = 900 / PICA_TO_MM
GRAND_MONDE_HEIGHT = 1260 / PICA_TO_MM

UNIVERS_WIDTH = 1000 / PICA_TO_MM
UNIVERS_HEIGHT = 1300 / PICA_TO_MM

# vim:set shiftwidth=4 softtabstop=4 spl=en:
