[EN] SLA document-able attributes
=================================

DOCUMENT
--------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT``.

+--------------------+-----------------------+-------------+-------------+----------+
| Path               | Explanation           | Value       | Default     | Optional |
+====================+=======================+=============+=============+==========+
| ``/@DPInCMYK``     | ICC profile for CMYK  | string      |             | Yes      |
|                    | images                |             |             |          |
+--------------------+-----------------------+-------------+-------------+----------+
| ``/@DPIn3``        | ICC profile for CMYK  | string      |             | Yes      |
|                    | colors                |             |             |          |
+--------------------+-----------------------+-------------+-------------+----------+
| ``/@PAGEC``        | Scribus GUI page      | hexadecimal | ``#ffffff`` |          |
|                    | background            | color       |             |          |
+--------------------+-----------------------+-------------+-------------+----------+

DOCUMENT/LAYERS
---------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT/LAYERS``.

+--------------+-----------------------+-------------+---------+----------+
| Path         | Explanation           | Value       | Default | Optional |
+==============+=======================+=============+=========+==========+
| ``/@FLOW``   |                       | integer     |         |          |
|              |                       | as boolean  |         |          |
+--------------+-----------------------+-------------+---------+----------+
| ``/@TRANS``  | Layer’s opacity       | percentage  | ``1``   |          |
|              |                       | 0 -> 1      |         |          |
+--------------+-----------------------+-------------+---------+----------+
| ``/@BLEND``  | Layer blend mode      |             |         |          |
+--------------+-----------------------+-------------+---------+----------+
| ``/@OUTL``   | Flag for wireframe    | integer     | ``0``   |          |
|              | view                  | as boolean  |         |          |
+--------------+-----------------------+-------------+---------+----------+
| ``/@LAYERS`` | Color outline of the  | hexadecimal |         |          |
|              | layer’s frames        | color       |         |          |
+--------------+-----------------------+-------------+---------+----------+

DOCUMENT/CHARSTYLE
------------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT/CHARSTYLE``.

+---------------------+--------------------+------------+---------+----------+
| Path                | Explanation        | Value      | Default | Optional |
+=====================+====================+============+=========+==========+
| ``/@DefaultStyle``  | Same as STYLE      | String     |         |          |
+---------------------+--------------------+------------+---------+----------+
| ``/@wordTrack``     | Space width        | Percentage |         |          |
|                     |                    |            |         |          |
|                     |                    | 0 -> 1     |         |          |
+---------------------+--------------------+------------+---------+----------+
| ``/@KERN``          | Kerning            | Percentage |         |          |
|                     |                    |            |         |          |
|                     |                    | 0 -> 100   |         |          |
+---------------------+--------------------+------------+---------+----------+
| ``/@HyphenWordMin`` | Minimal number of  | Integer    |         |          |
|                     |                    |            |         |          |
|                     | caracters for word | >= 3       |         |          |
|                     |                    |            |         |          |
|                     | for word           |            |         |          |
|                     | hyphenation        |            |         |          |
+---------------------+--------------------+------------+---------+----------+

DOCUMENT/Sections
-----------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT/Sections/Section``.

+------------------+-------------+--------------------+------------------+----------+
| Path             | Explanation | Value              | Default          | Optional |
+==================+=============+====================+==================+==========+
| ``/@FillChar``   |             | Unicode code       | ``0``            |          |
|                  |             |                    |                  |          |
|                  |             | point of character | (NULL character) |          |
+------------------+-------------+--------------------+------------------+----------+
| ``/@FieldWidth`` |             |                    | ``0``            |          |
+------------------+-------------+--------------------+------------------+----------+

DOCUMENT/PAGEOBJECT
-------------------

Omitted XPath : ``/SCRIBUSUTF8NEW/DOCUMENT/PAGEOBJECT``.

+--------------------------+--------------------+--------------------+---------+----------+
| Path                     | Explanation        | Value              | Default | Optional |
+==========================+====================+====================+=========+==========+
| ``/@path``               | Path data          | SVG path/@d string | ``0``   |          |
+--------------------------+--------------------+--------------------+---------+----------+
| ``/@copath``             | Path data          | Same as @path      |         |          |
+--------------------------+--------------------+--------------------+---------+----------+
| ``[@PTYPE="4"]/@VAlign`` | Vertical alignment | Same as @path      | ``0``   | No       |
|                          |                    |                    |         |          |
|                          | of the text within | 0 = top            |         |          |
|                          |                    |                    |         |          |
|                          | the frame          | 1 = center         |         |          |
|                          |                    |                    |         |          |
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
