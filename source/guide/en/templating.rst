PyScribus templating
====================

What you can do with PyScribus templating
-----------------------------------------

- Find appropriate page object with page object attributes
- Inject text into text frames stories

Activation & configuration
--------------------------

To activate templating features of PyScribus, first add the parameter 
``templating`` to the SLA object (pyscribus.sla.SLA) :

  ::

   import pyscribus.sla as sla

   # intro.sla is parsed at instanciation
   parsed = sla.SLA("template.sla", "1.5.5", templating=True)

You can set some other templating parameters, but there is already parameters 
defined.

+-----------------------+---------------------------+---------------+
| Kwarg key             | Use                       | Default value |
+=======================+===========================+===============+
| templatingInsensitive | Should in-text templating | False         |
|                       | be case insensitive ?     |               |
+-----------------------+---------------------------+---------------+
| templatingPattern     | compiled regex to find    | \^%\w+%$      |
|                       | templated elements        |               |
|                       | (ex: %TITLE%)             |               |
+-----------------------+---------------------------+---------------+

Load data
---------
