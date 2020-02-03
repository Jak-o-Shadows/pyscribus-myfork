[FR] Comment les *stories* de Scribus (semblent) fonctionner
============================================================

Les *stories* de Scribus sont contenues dans des éléments XML
``StoryText`` et comportent en séquence les élements XML suivants :

================ ========================
Élement XML      Usage
================ ========================
``DefaultStyle`` Remise à zéro des styles
``ITEXT``        Fragment de texte
``para``         Fin de paragraphe
``MARK``         Marque de référence
``breakline``    Retour à la ligne forcé
``trail``        Fin de *story*
================ ========================

``DefaultStyle`` remet les styles à zéro et est systématiquement le
premier enfant de ``StoryText`` (sans doute pour éviter une
contamination des styles à la suite d’une erreur).

Comment faire un paragraphe
---------------------------

Les *stories* de Scribus n’emploient pas d’éléments XML imbriqués, pas
plus qu’ils n’emploient d’éléments XML ayant un contenu (tout se passe
dans les attributs, c’est une tendance générale du SLA).

On ne peut donc pas repérer un paragraphe parce qu’il constitue un
élement XML unique.

.. note:: En fait si, mais seulement si le paragraphe est vide.

Un paragraphe d’une *story* Scribus est une séquence de fragments de
texte ayant des caractéristiques de mises en forme différentes, de
marqueurs de retour à la ligne manuels, de marques de références, se
terminant par un marqueur de fin de paragraphe.

Ainsi le paragraphe suivant :

   | Scribus est un *logiciel*
   | libre.

donnera dans une *story* :

.. code:: xml

   <ITEXT CH="Scribus est un " />
   <ITEXT FONT="Arial Italic" CH="logiciel" />
   <breakline />
   <ITEXT CH="libre" />
   <para/>

Et un paragraphe vide donnera :

.. code:: xml

   <para/>
   <para/>

…où le premier ``para`` est la fin du paragraphe précédent (vide ou
non).
