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

__all__ = ['fill_nan_pixels',
           'image_files_in_dir',
           'image_files_in_paths',
           'load_image',
           'save_image']

import numpy as np

import os

from pywi.io.pil import load_pil_image, save_pil_image
from pywi.io.fits import load_fits_image, save_fits_image
from pywi.io.plot import plot

DEBUG = False


# FILL NAN PIXELS #############################################################

def fill_nan_pixels(image, noise_distribution=None):
    """Replace *in-place* `NaN` values in `image` by zeros or by random noise.

    Images containing `NaN` values generate undesired harmonics with wavelet
    image cleaning. This function should be used to "fix" images before each
    wavelet image cleaning.

    Replace `NaN` ("Not a Number") values in `image` by zeros if
    `noise_distribution` is `None`.
    Otherwise, `NaN` values are replaced by random noise drawn by the
    `noise_distribution` random generator.

    Parameters
    ----------
    image : array_like
        The image to process. `NaN` values are replaced **in-place** thus this
        function changes the provided object.
    noise_distribution : `pywi.denoising.inverse_transform_sampling.EmpiricalDistribution`
        The random generator to use to replace `NaN` pixels by random noise.

    Returns
    -------
    array_like
        Returns a boolean mask array indicating whether pixels in `images`
        initially contained `NaN` values (`True`) of not (`False`). This array
        is defined by the instruction `np.isnan(image)`.

    Notes
    -----
        `NaN` values are replaced **in-place** in the provided `image`
        parameter.

    Examples
    --------
    >>> import numpy as np
    >>> img = np.array([[1, 2, np.nan],[4, np.nan, 6],[np.nan, 8, np.nan]])
    >>> fill_nan_pixels(img)
    ... # doctest: +NORMALIZE_WHITESPACE
    array([[False, False,  True],
           [False,  True, False],
           [ True, False,  True]], dtype=bool)
    >>> img
    ... # doctest: +NORMALIZE_WHITESPACE
    array([[ 1., 2., 0.],
           [ 4., 0., 6.],
           [ 0., 8., 0.]])
    """

    # See https://stackoverflow.com/questions/29365194/replacing-missing-values-with-random-in-a-numpy-array
    nan_mask = np.isnan(image)

    if DEBUG:
        print(image)
        plot(image, "In")
        plot(nan_mask, "Mask")

    if noise_distribution is not None:
        nan_noise_size = np.count_nonzero(nan_mask)
        image[nan_mask] = noise_distribution.rvs(size=nan_noise_size)
    else:
        image[nan_mask] = 0

    if DEBUG:
        print(image)
        plot(image, "Noise injected")

    return nan_mask


# DIRECTORY PARSER ############################################################

def image_files_in_dir(directory_path, max_num_files=None, file_ext=(".fits", ".fit")):
    """Return the path of FITS and Simtel files in `directory_path`.

    Return the path of all (or `max_num_files`) files having the extension
    ".simtel", ".simtel.gz", ".fits" or ".fit" in `directory_path`.

    Parameters
    ----------
    directory_path : str
        The directory's path where FITS and Simtel files are searched.
    max_num_files : int
        The maximum number of files to return.

    Yields
    ------
    str
        The path of the next FITS or Simtel files in `directory_path`.
    """

    directory_path = os.path.expanduser(directory_path)

    files_counter = 0

    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith(file_ext):
            files_counter += 1
            if (max_num_files is not None) and (files_counter > max_num_files):
                break
            else:
                yield file_path


def image_files_in_paths(path_list, max_num_files=None):
    """Return the path of FITS and Simtel files in `path_list`.

    Return the path of all (or `max_num_files`) files having the extension
    ".simtel", ".simtel.gz", ".fits" or ".fit" in `path_list`.

    Parameters
    ----------
    path_list : str
        The list of directory's path where FITS and Simtel files are searched.
        It can also directly contain individual file paths (or a mix of files
        and directories path).
    max_num_files : int
        The maximum number of files to return.

    Yields
    ------
    str
        The path of the next FITS or Simtel files in `path_list`.
    """

    files_counter = 0

    for path in path_list:
        if os.path.isdir(path):
            # If path is a directory
            for file_path in image_files_in_dir(path):
                files_counter += 1
                if (max_num_files is not None) and (files_counter > max_num_files):
                    break
                else:
                    yield file_path
        elif os.path.isfile(path):
            # If path is a regular file
            files_counter += 1
            if (max_num_files is not None) and (files_counter > max_num_files):
                break
            else:
                yield path
        else:
            raise Exception("Wrong item:", path)


# LOAD AND SAVE FITS FILES ###################################################

def load_image(input_file_path, **kwargs):
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
    
    if input_file_path.lower().endswith((".fits", ".fit")):
        # FITS FILES
        image_array = load_fits_image(input_file_path, **kwargs)
    else:
        image_array = load_pil_image(input_file_path, **kwargs)

    return image_array


def save_image(image_array, output_file_path, **kwargs):
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
    
    if output_file_path.lower().endswith((".fits", ".fit")):
        # FITS FILES
        save_fits_image(image_array, output_file_path)
    else:
        save_pil_image(image_array, output_file_path)


# DEBUG #######################################################################

def export_image_as_plain_text(image, output_file_path):
    fd = open(output_file_path, 'w')
    for x in image:
        for y in x:
            print("{:5.2f}".format(y), end=" ", file=fd)
        print("", file=fd)
    fd.close()
