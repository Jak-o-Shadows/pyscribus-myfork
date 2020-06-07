[FR] Mesures et autres nombres
==============================

Les mesures employées dans le SLA sont

-  le point DTP/pica (soit 25,4 / 72 mm)
-  le pourcentage
-  une unité sans nom (!) où 1 = 1/72 pouce (*inch*), qui sert à
   localiser les objets dans l’espace (X positif à droite, Y positif en
   bas).
-  Le degré / angle normal (0-360)
-  Le degré / angle de plume calligraphique (0-180)
-  Le point par pouce (PPP, PPI, DPI), de 0 à l’infini positif.

L’objet Dim manipule ces unités, permettant de renvoyer des valeurs
valides dans le SLA, et de mieux appréhender les mesures (une page de
595.275… × 841.889… points pica est une page de 210 × 297 mm, soit une A4 portrait).
