#!/bin/bash
cd source/
python3 -m twine upload --repository pypi dist/*
