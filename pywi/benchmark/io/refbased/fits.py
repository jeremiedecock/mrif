#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016,2017,2018 Jérémie DECOCK (http://www.jdhp.org)

# This script is provided under the terms and conditions of the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ = ['load_benchmark_images']

from astropy.io import fits

import numpy as np

# LOAD FITS BENCHMARK IMAGE ##################################################

def load_benchmark_images(input_file_path):
    """Return images contained in the given FITS file.

    Parameters
    ----------
    input_file_path : str
        The path of the FITS file to load

    Returns
    -------
    dict
        A dictionary containing the loaded images and their metadata

    Raises
    ------
    WrongFitsFileStructure
        If `input_file_path` doesn't contain a valid structure
    """

    hdu_list = fits.open(input_file_path)   # open the FITS file

    # IMAGES ##################################################################

    if (len(hdu_list) != 2) or (not hdu_list[0].is_image) or (not hdu_list[1].is_image):
        hdu_list.close()
        raise WrongFitsFileStructure(input_file_path)

    hdu0, hdu1 = hdu_list

    images_dict = {}

    images_dict["image"] = hdu0.data        # "hdu.data" is a Numpy Array
    images_dict["reference"] = hdu1.data    # "hdu.data" is a Numpy Array

    hdu_list.close()

    return images_dict
