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
|                       |                           |               |
|                       | (ex: %TITLE%)             |               |
+-----------------------+---------------------------+---------------+

Load data
---------

  ::

   # Getting all stories with template-able content
   # Return a list of stories
   stories = parsed.templatable_stories()

   datas = [
       {
           "%Title%": "My title",
           "%Text%": "Lorem ipsum"
       }
   ]

   # For each stories, we replace/feed the placeholders with their contents

   for index, templatable_story in enumerate(stories):
       templatable_story.feed_templatable(datas[index])

   # Saving the templated document as a new one

   template.save("templated.sla")
