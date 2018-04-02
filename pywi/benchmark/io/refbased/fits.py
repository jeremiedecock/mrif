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

__all__ = ['BenchmarkImage',
           'benchmark_image_generator',
           'load_benchmark_images']

from astropy.io import fits

import collections

import numpy as np

from pywi.io.images import image_files_in_paths


# IMAGE OBJECT ###############################################################

BenchmarkImage = collections.namedtuple('BenchmarkImage', ('input_image',
                                                           'reference_image',
                                                           'metadata'))


# IMAGE GENERATOR ############################################################

def benchmark_image_generator(path_list,
                              max_num_images=None,
                              **kwargs):
    """Return an iterable sequence all calibrated images in `path_list`.

    Parameters
    ----------
    path_list
        The path of files containing the images to extract. It can contain
        FITS/Simtel files and directories.
    max_num_images
        The maximum number of images to iterate.

    Yields
    ------
    Image1D or Image2D
        The named tuple `Image1D` or `Image1D` of the next FITS or Simtel files
        in `path_list`.
    """

    images_counter = 0

    for file_path in image_files_in_paths(path_list):
        if (max_num_images is not None) and (images_counter >= max_num_images):
            break
        else:
            if file_path.lower().endswith((".fits", ".fit")):
                # FITS FILES
                benchmark_image = load_benchmark_images(file_path)
                images_counter += 1
                yield benchmark_image
            else:
                raise Exception("Wrong item:", file_path)


# LOAD FITS BENCHMARK IMAGE ##################################################

def load_benchmark_images(file_path):
    """Return images contained in the given FITS file.

    Parameters
    ----------
    file_path : str
        The path of the FITS file to load

    Returns
    -------
    dict
        A dictionary containing the loaded images and their metadata

    Raises
    ------
    WrongFitsFileStructure
        If `file_path` doesn't contain a valid structure
    """

    hdu_list = fits.open(file_path)   # open the FITS file

    # METADATA ################################################################

    hdu0 = hdu_list[0]

    metadata = {}

    for key, val in hdu0.header.items():
        metadata[key] = val

    # IMAGES ##################################################################

    if (len(hdu_list) != 2) or (not hdu_list[0].is_image) or (not hdu_list[1].is_image):
        hdu_list.close()
        raise WrongFitsFileStructure(file_path)

    hdu0, hdu1 = hdu_list

    input_image = hdu0.data        # "hdu.data" is a Numpy Array
    reference_image = hdu1.data    # "hdu.data" is a Numpy Array

    hdu_list.close()

    benchmark_image = BenchmarkImage(input_image=input_image,
                                     reference_image=reference_image,
                                     metadata=metadata)

    return benchmark_image
