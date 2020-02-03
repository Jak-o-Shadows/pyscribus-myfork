[FR] Fonctionnement général
===========================

Tous les objets de pyscribus correspondant à un élement XML du SLA ont
comme méthodes :

-  ``toxml`` renvoyant un lxml.etree._Element conforme au SLA
-  ``fromxl`` analysant un lxml.etree_Element
-  ``fromdefault`` avec éventuellement un argument ``default``, pour
   obtenir les valeurs d’un fichier SLA par défaut. S’il y a plusieurs
   élements par défaut correspondant à cet objet (par exemple, il y a
   plusieurs couleurs par défaut définies), ``default`` sert à spécifier
   quel ensemble de valeurs choisir (par exemple, ``"Black"``).
