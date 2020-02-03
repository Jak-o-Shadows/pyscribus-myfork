*****************************
SLA's enhancement suggestions
*****************************

# 1
===

The case used of element names and attributes should be clearly defined and homogeneous.

Discussion
----------

Almost every text case is used for element's names attributes. But XML/XSL tools 
are case sensitive by default.

Why ``DOCUMENT/MASTERPAGE``, ``DOCUMENT/PAGEOBJECT/LATEX/PROPERTY``, 
``DOCUMENT/Sections/Section`` ?

# 2
===

Render frames buffers should use a generic element name instead of `LATEX`, 
as they link to a configuration file and they no more render only LaTeX code.

Discussion
----------

It makes no sense to have a LATEX element with GnuPlot instructions.

# 3
===

Attribute names should be in only one language, so the remaining german 
attributes should be translated.

Discussion
----------

``<LAYERS NUMMER="0" LEVEL="0" NAME="Fond de page" SICHTBAR="1" DRUCKEN="1" EDIT="1" SELECT="0" FLOW="1" TRANS="1" BLEND="0" OUTL="0" LAYERC="#000000"/>``
