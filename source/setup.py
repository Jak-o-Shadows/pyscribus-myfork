#!/usr/bin/python3
# -*- coding:Utf-8 -*-

import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyscribus",
    version="0.1",
    author="Etienne Nadji",
    author_email="etnadji@eml.cc",
    description="Read, create and update Scribus .sla files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://etnadji.fr/pyscribus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Text Processing :: Markup :: XML",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.6',
    install_requires=['lxml'],
)

# vim:set shiftwidth=4 softtabstop=4 spl=en:
