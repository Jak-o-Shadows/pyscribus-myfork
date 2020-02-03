#!/usr/bin/python3
# -*- coding:Utf-8 -*-

"""
Test loading styles of an existing SLA and applying them to a new SLA file.
"""

import pyscribus.sla as sla
import pyscribus.styles as styles

if __name__ == "__main__":
    # Import the styles of a existing file

    s = styles.fromSLA("tests/styles.sla")

    # Create a SLA file from scratch
    testfile = sla.SLA(version="1.5.5")
    testfile.fromdefault()

    # Add the imported files to it
    testfile.documents[0].styles = s

    # Save the new file
    testfile.save("tests-outputs/test-styles-import.sla")

# vim:set shiftwidth=4 softtabstop=4:
