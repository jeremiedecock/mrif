#!/bin/sh

# DOCTESTS ####################################################################

echo
echo
python3 -m doctest ./pywi/io/images.py
if [ $? -ne 0 ]; then
    exit 1
fi

echo
echo
python3 -m doctest ./pywi/processing/filtering/pixel_clusters.py
if [ $? -ne 0 ]; then
    exit 1
fi

# UNITTESTS ###################################################################

pytest
