[EN] SLA document-able attributes
=================================

DOCUMENT
--------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT``.

+--------------------+-----------------------+--------------------+-------------+----------+
| XML                | Explanation           | Value              | Default     | Optional |
| element/attribute  |                       |                    |             |          |
+====================+=======================+====================+=============+==========+
| ``/@DPInCMYK``     | ICC profile for CMYK  | string             |             | Yes      |
|                    | images                |                    |             |          |
+--------------------+-----------------------+--------------------+-------------+----------+
| ``/@DPIn3``        | ICC profile for CMYK  | string             |             | Yes      |
|                    | colors                |                    |             |          |
+--------------------+-----------------------+--------------------+-------------+----------+
| ``/@PAGEC``        | Scribus GUI page      | hexadecimal color  | ``#ffffff`` |          |
|                    | background            |                    |             |          |
+--------------------+-----------------------+--------------------+-------------+----------+
| ``/LAYERS/@FLOW``  |                       | integer as boolean |             |          |
+--------------------+-----------------------+--------------------+-------------+----------+
| ``/LAYERS/@TRANS`` | Layer’s opacity       | percentage         | ``1``       |          |
|                    |                       | 0 -> 1             |             |          |
+--------------------+-----------------------+--------------------+-------------+----------+

DOCUMENT/LAYERS
---------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT``.

+---------------------+-----------------------+--------------------+---------+----------+
| XML                 | Explanation           | Value              | Default | Optional |
| element/attribute   |                       |                    |         |          |
+=====================+=======================+====================+=========+==========+
| ``/LAYERS/@BLEND``  | Layer blend mode      |                    |         |          |
+---------------------+-----------------------+--------------------+---------+----------+
| ``/LAYERS/@OUTL``   | Flag for wireframe    | integer as boolean | ``0``   |          |
|                     | view                  |                    |         |          |
+---------------------+-----------------------+--------------------+---------+----------+
| ``/LAYERS/@LAYERS`` | Color outline of the  | hexadecimal color  |         |          |
|                     | layer’s frames        |                    |         |          |
+---------------------+-----------------------+--------------------+---------+----------+

DOCUMENT/CHARSTYLE
------------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT``.

+------------------------------+--------------------+------------+---------+----------+
| XML                          | Explanation        | Value      | Default | Optional |
| element/attribute            |                    |            |         |          |
+==============================+====================+============+=========+==========+
| ``/CHARSTYLE/@DefaultStyle`` | Same as STYLE, but | string     |         |          |
|                              | not documented     |            |         |          |
+------------------------------+--------------------+------------+---------+----------+
| ``/CHARSTYLE/@wordTrack``    | Space width        | Percentage |         |          |
|                              |                    | 0 -> 1     |         |          |
+------------------------------+--------------------+------------+---------+----------+
| ``/CHARSTYLE/@KERN``         | Kerning            | Percentage |         |          |
|                              |                    | 0 -> 100   |         |          |
+------------------------------+--------------------+------------+---------+----------+

DOCUMENT/Sections
-----------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT``.

+-------------------------------------+-------------+--------------------+------------------+----------+
| XML                                 | Explanation | Value              | Default          | Optional |
| element/attribute                   |             |                    |                  |          |
+=====================================+=============+====================+==================+==========+
| ``/Sections/Section/@FillChar``     |             | Unicode code       | ``0``            |          |
|                                     |             | point of character | (NULL character) |          |
+-------------------------------------+-------------+--------------------+------------------+----------+
| ``/Sections/Section/@FieldWidth``   |             |                    | ``0``            |          |
+-------------------------------------+-------------+--------------------+------------------+----------+

DOCUMENT/PAGEOBJECT
-------------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT/PAGEOBJECT``.

+--------------------------+--------------------+--------------------+---------+----------+
| XML                      | Explanation        | Value              | Default | Optional |
| element/attribute        |                    |                    |         |          |
+==========================+====================+====================+=========+==========+
| ``/@path``               | Path data          | SVG path/@d string | ``0``   |          |
+--------------------------+--------------------+--------------------+---------+----------+
| ``/@copath``             | Path data          | Same as @path      |         |          |
+--------------------------+--------------------+--------------------+---------+----------+
| ``[@PTYPE="4"]/@VAlign`` | Vertical alignment | Same as @path      | ``0``   | No       |
|                          | of the text within | 0 = top            |         |          |
|                          | the frame          | 1 = center         |         |          |
|                          |                    | 2 = bottom         |         |          |
+--------------------------+--------------------+--------------------+---------+----------+

Notes
-----

``/PAGEOBJECT/@path`` and ``/PAGEOBJECT/@copath`` format specifications are 
`available on W3C <https://www.w3.org/TR/SVG/paths.html#TheDProperty>`_.

Attributes ``@RATIO``, ``@SCALETYPE``, ``@LOCALSCX``, ``@LOCALSCY``, 
``@LOCALX``, ``@LOCALY``, ``@LOCALROT``, ``@PICART`` 
of ``/PAGEOBJECT/`` are **not** optional.

Corrections
-----------

For ``Sections/Section/@Type``, the possible values are incomplete in the wiki.

The complete possible values are :

- Type_1_2_3
- Type_1_2_3_ar
- Type_i_ii_iii
- Type_I_II_III
- Type_a_b_c
- Type_A_B_C
- Type_Alphabet_ar
- Type_Abjad_ar
- Type_Hebrew
- Type_asterix
- Type_CJK

Notable things
--------------

``/Marks/Mark[@type="3"]`` (variable text mark) ``@str`` attribute is used like 
the ``@label`` attribute of ``/Marks/Mark[@type!="3"]``.
