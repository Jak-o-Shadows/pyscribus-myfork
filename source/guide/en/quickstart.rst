**********
Quickstart
**********

Install PyScribus
=================

Pip
---

PyScribus is available through pip :

**For Python versions >= 3.8 :**

``pip install pyscribus``

**For older Python versions :**

``pip install -i https://test.pypi.org/simple/ pyscribus-backported``

Git
---

The code of PyScribus is available as a GIT repository on Framagit.

``git clone https://framagit.org/etnadji/pyscribus.git``

An introduction to PyScribus modules
====================================

Used for parsing & generating
-----------------------------

+-------------+-------------------------------+
| Module      | Use                           |
+=============+===============================+
| sla         | SLA file                      |
+-------------+-------------------------------+
| document    | SLA document                  |
+-------------+-------------------------------+
| dimensions  | Measures used in SLA          |
+-------------+-------------------------------+
| colors      | Colors and gradients          |
+-------------+-------------------------------+
| patterns    | Patterns                      |
+-------------+-------------------------------+
| pages       | Pages                         |
+-------------+-------------------------------+
| pageobjects | Page objects                  |
+-------------+-------------------------------+
| marks       | Marks                         |
+-------------+-------------------------------+
| stories     | Stories                       |
+-------------+-------------------------------+
| notes       | Notes                         |
+-------------+-------------------------------+
| styles      | SLA styles                    |
+-------------+-------------------------------+
| toc         | Sections & Tables of contents |
+-------------+-------------------------------+
| printing    | Printing settings             |
+-------------+-------------------------------+

Paper sizes
-----------

Theses modules define the width and height of many paper formats in the unit
Scribus handle (See **Measures and geometry in PyScribus**).

You will just need ``papers.iso216`` if you don't work in an 
american / canadian context.

+---------------+---------------------------+---------------------------+
| Module        | Use                       | Examples                  |
+===============+===========================+===========================+
| papers.iso216 | ISO 216 sizes (A, B)      | A4; A3                    |
+---------------+---------------------------+---------------------------+
| papers.iso269 | ISO 269 sizes (C, DL)     | C6; DL                    |
+---------------+---------------------------+---------------------------+
| papers.iso217 | ISO 217 sizes (RA, SRA)   | RAO; 2SRA0                |
+---------------+---------------------------+---------------------------+
| papers.ansi   | ANSI normalized sizes.    | Letter / ANSI A           |
+---------------+---------------------------+---------------------------+
| papers.afnor  | AFNOR normalized sizes    | Raisin; Jesus             |
+---------------+---------------------------+---------------------------+

Extras
------

Theses modules are shipped with PyScribus but may requires other python 
libraries.

+-------------+-----------------------+----------------------------------------+
| Module      | Use                   | Additionnal requirements               |
+=============+=======================+========================================+
| wireframe   | Drawing SLA wireframe | `Pillow <https://python-pillow.org/>`_ |
+-------------+-----------------------+----------------------------------------+

Basis
-----

Theses "low-level" (XML utilities and abstract classes) modules are used by 
most of the other ones.

+-------------+-------------------------------+
| Module      | Use                           |
+=============+===============================+
| common.xml  | Common XML parsing utilities  |
+-------------+-------------------------------+
| common.math | Common math values            |
+-------------+-------------------------------+
| exceptions  | PyScribus exceptions          |
+-------------+-------------------------------+

Basics of PyScribus objects
===========================

Each PyScribus object corresponding to a objet in the SLA source file, for 
example, a color definition, a paragraph style… has some common methods.

Defaults
--------

You can import default attributes of a PyScribus object with `.fromdefault` 
method. Sometimes, there is not one set of defaults attributes but many (for 
example, the colors included in every new Scribus document); in that case, you 
would find the set name with `.listdefaults` method and 
in `pyscribus_defaults` attributes.

  ::

   import pyscribus.colors as colors

   black = colors.Color()

   black.listdefaults()

   # ['Black',
   #  'Blue',
   #  'Cool Black',
   #  'Cyan',
   #  'Green',
   #  'Magenta',
   #  'Red',
   #  'Registration',
   #  'Rich Black',
   #  'Warm Black',
   #  'White',
   #  'Yellow']

   # For the Color object, no set name -> Black set.
   black.fromdefault()
   # {'C': 0.0, 'M': 0.0, 'Y': 0.0, 'K': 100.0}, True
   print(black.colors, black.is_cmyk)

   red = colors.Color()
   # Red, Green, Blue are default colors in RGB color space
   red.fromdefault("Red")
   # {'R': 255.0, 'G': 0.0, 'B': 0.0}, False
   print(red.colors, red.is_cmyk)

XML
---

The SLA file format is an XML one. So if you only want to convert a portion 
of a SLA file into a Python object, you can do that with the `.fromxml` method.

  ::

   import lxml.etree as ET

   import pyscribus.colors as colors

   # SLA color definition -----------------------

   code = '<COLOR NAME="Black" SPACE="CMYK" C="0" M="0" Y="0" K="100"/>'

   # Create the color object and load from code -

   source = ET.fromstring(code)

   color = colors.Color()
   color.fromxml(source)

   # --------------------------------------------

   # {'C': 0.0, 'M': 0.0, 'Y': 0.0, 'K': 100.0}, True
   print(color.colors, color.is_cmyk)


Measures and geometry in PyScribus
==================================

As Scribus is used among users of metric and imperial systems, it must manage
length notation through a common unit in the SLA format (not in Scribus GUI),
which is the pica points, equally unknown to anyone but DTP softwares.

To manage the 8 units for lengths and numeric values in SLA, PyScribus use 
the `dimensions.Dim` object. For frames and pages, PyScribus use 
`dimensions.DimBox`.

Frequent tasks
==============

Reading an existing SLA file
----------------------------

  ::

   import pyscribus.sla as sla

   # intro.sla is parsed at instanciation
   parsed = sla.SLA("intro.sla", "1.5.5")

Generating an SLA file
----------------------

  ::

   import pyscribus.sla as sla

   generated = sla.SLA(version="1.5.5")

   # Loading default content and settings
   generated.fromdefault()

   # Here you can do some modifications

   # Then :
   # Saving
   generated.save("generated.sla")

Creating a frame (page object)
------------------------------

Adding things to a SLA file
---------------------------

You can access SLA datas through object attributes, but most of the time, if you 
want to append something (document, pages, master pages, layers, colors, page 
objects and styles), use the ``SLA.append()`` function.

