#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Jérémie DECOCK (http://www.jdhp.org)

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

__all__ = ['load_fits_image',
           'save_fits_image']

from astropy.io import fits


def load_fits_image(input_file_path, hdu_index=0):
    """Return the image array contained in the given HDU of the given FITS file.

    Parameters
    ----------
    input_file_path : str
        The path of the FITS file to load
    hdu_index : int
        The HDU to load within the FITS file (one FITS file can contain several
        images stored in different HDU)

    Returns
    -------
    ndarray
        The loaded image

    Raises
    ------
    WrongHDUError
        If `input_file_path` doesn't contain the HDU `hdu_index`
    NotAnImageError
        If `input_file_path` doesn't contain a valid image in the HDU
        `hdu_index`
    """
    
    hdu_list = fits.open(input_file_path)   # open the FITS file

    if not (0 <= hdu_index < len(hdu_list)):
        hdu_list.close()
        raise WrongHDUError(input_file_path, hdu_index)

    hdu = hdu_list[hdu_index]

    if not hdu.is_image:
        hdu_list.close()
        raise NotAnImageError(input_file_path, hdu_index)

    image_array = hdu.data    # "hdu.data" is a Numpy Array

    hdu_list.close()

    return image_array


def save_fits_image(image_array, output_file_path):
    """Save the `image_array` image (array_like) to the `output_file_path` FITS file.

    Parameters
    ----------
    image_array : array_like
        The image to save (should be a 2D or a 3D numpy array)
    output_file_path : str
        The path of the FITS file where to save the `image_array`

    Raises
    ------
    WrongDimensionError
        If `image_array` has more than 3 dimensions or less than 2 dimensions.
    """

    if image_array.ndim not in (2, 3):
        raise WrongDimensionError()

    hdu = fits.PrimaryHDU(image_array)

    hdu.writeto(output_file_path, overwrite=True)  # overwrite=True: overwrite the file if it already exists
