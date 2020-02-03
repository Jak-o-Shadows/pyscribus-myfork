#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Templating system test for PyScribus.

Produce test-templated.sla using tests/templating.sla
as template document.
"""

import pyscribus.sla as sla

if __name__ == "__main__":
    # templating=True activate templating functions

    template = sla.SLA(
        "tests/templating.sla",
        "1.5.5",
        templating=True
    )

    # The data that will be injected into the document

    datas = [
        {
            "%Title%": "An editorial",
            "%Lead%": "I know better than everyone of you",
            "%Text%": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "%Following%": "p. 4"
        },
        {
            "%Title%": "First article title",
            "%Lead%": "This article is about stuff.",
            "%Text%": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "%Following%": "p. 5"
        },
        {
            "%Title%": "Second article title",
            "%Lead%": "This is fake news.",
            "%Text%": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            "%Following%": "p. 5"
        },
    ]

    # Get all stories of the template that contains
    # template-able elements.

    # Templatable in-text elements are found with a regular
    # expression defined in sla.SLA.templating, like other
    # templating options.

    # We use the default regular expression here so
    # placeholders are surrounded by %

    # The search for placeholders is also case insensitive
    # by default.

    stories = template.templatable_stories()

    # Iterate over each story that contains template-able elements,
    # and injects the datas.

    for idx, templatable_story in enumerate(stories):
        templatable_story.feed_templatable(datas[idx])

    # Save the new document

    template.save("tests-outputs/test-templated.sla")

# vim:set shiftwidth=4 softtabstop=4:
