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

__all__ = ['load_pil_image',
           'save_pil_image']

import numpy as np

import PIL.Image as pil_image     # PIL.Image is a module not a class...


def normalize(array):
    """Normalize the values of a Numpy array in the range [0,1].

    Parameters
    ----------
    array : array like
        The array to normalize

    Returns
    -------
    ndarray
        The normalized array
    """
    min_value = array.min()
    max_value = array.max()
    size = max_value - min_value

    if size > 0:
        array = array.astype('float64', copy=True)
        norm_array = (array - min_value)/size
    else:
        norm_array = array

    return norm_array


def load_pil_image(input_file_path):
    """Return the image array contained in the given image file.

    So far, this function convert all multi-channel input images as
    mono-channel grayscale.

    The list of supported formats is available in the following page:
    https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

    Fits format is also supported thanks to astropy.

    Parameters
    ----------
    input_file_path : str
        The path of the image file to load

    Returns
    -------
    ndarray
        The loaded image
    """
    
    pil_img = pil_image.open(input_file_path)
    pil_img = pil_img.convert('L')
    image_array = np.array(pil_img)  # It works also with .png, .jpg, tiff, ...

    return image_array


def save_pil_image(image_array, output_file_path):
    """Save the image array `image` in the given file `output_file_path`.

    The list of supported formats is available in the following page:
    https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

    Fits format is also supported thanks to astropy.

    Parameters
    ----------
    image : array_like
        The image to save
    output_file_path : str
        The destination path of the image
    """
    
    mode = "L"              # Grayscale
    size_y, size_x = image_array.shape
    pil_img = pil_image.new(mode, (size_x, size_y))

    # Make the data (pixels value in [0;255])
    # WARNING: nested list and 2D numpy arrays are silently rejected!!!
    #          data *must* be a list or a 1D numpy array!
    image_array = normalize(image_array) * 255.
    image_array = image_array.astype('uint8', copy=True)

    pil_img.putdata(image_array.flatten())
    pil_img.save(output_file_path)
