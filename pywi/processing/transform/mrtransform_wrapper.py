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

__all__ = ['MrTransformError',
           'WrongDimensionError',
           'wavelet_transform',
           'inverse_wavelet_transform']

"""Denoise images with Wavelet Transform.

This module is a wrapper for mr_transform -- a program written CEA/CosmoStat
(www.cosmostat.org) -- to make Wavelet Transform.

Notes
-----
This script requires the mr_transform program
(http://www.cosmostat.org/software/isap/).

It also requires the Numpy library.
"""

import copy
import numpy as np
import os
import time

from pywi.io import images
from pywi.io import fits

# CONSTANTS ##################################################################

AVAILABLE_LAST_SCALE_OPTIONS = ('keep', 'drop', 'mask')
DEFAULT_LAST_SCALE_TREATMENT = 'mask'

# EXCEPTIONS #################################################################

class MrTransformError(Exception):
    """Common `wavelet_mrtransform` module's error."""
    pass

class WrongDimensionError(MrTransformError):
    """Raised when data having a wrong number of dimensions is given.

    Attributes
    ----------
    msg : str
        Explanation of the error.
    """

    def __init__(self, msg=None):
        if msg is None:
            self.msg = "The data has a wrong number of dimension."


##############################################################################

def wavelet_transform(input_image,
                      number_of_scales=4,
                      tmp_files_directory=".",
                      noise_distribution=None,
                      debug=False):
    """Compute the wavelet transform of `input_image`.

    Parameters
    ----------
    input_image : array_like
        The input image to transform.
    number_of_scales : int, optional
        The number of scales used to transform `input_image` or in other words
        the number of wavelet planes returned.
    tmp_files_directory : str, optional
        The path of the directory used to store mr_transform temporary data.
        The default is the current directory, but it may be more appropriate to
        specify here the path of a directory mounted in a ramdisk to speedup
        I/Os ("/Volumes/ramdisk" on MacOSX or "/dev/shm" on Linux).
    noise_distribution : `EmpiricalDistribution`, optional
        The noise distribution used to fill 'empty' NaN pixels with the
        appropriate random noise distribution. If none, NaN pixels are fill
        with zeros (which may add unwanted harmonics in wavelet planes).

    Returns
    -------
    list
        Return a list containing the wavelet planes.

    Raises
    ------
    WrongDimensionError
        If `input_image` is not a 2D array.
    """

    input_image = input_image.copy()

    if input_image.ndim != 2:
        msg = "The data should be a 2D array."
        raise WrongDimensionError(msg)

    # INJECT NOISE IN NAN PIXELS ###########################################

    # TODO: should this noise injection be done in the abstract 'run()' function ?

    nan_mask = images.fill_nan_pixels(input_image, noise_distribution)

    # DO THE WAVELET TRANSFORM #############################################

    input_file_name = ".tmp_{}_{}_in.fits".format(os.getpid(), time.time())
    input_file_path = os.path.join(tmp_files_directory, input_file_name)

    output_file_name = ".tmp_{}_{}_out.fits".format(os.getpid(), time.time())
    mr_output_file_path = os.path.join(tmp_files_directory, output_file_name)

    try:
        # WRITE THE INPUT FILE (FITS) ##########################

        fits.save_fits_image(input_image, input_file_path)

        # EXECUTE MR_TRANSFORM #################################

        cmd = 'mr_transform -n{} "{}" {}'.format(number_of_scales,
                                                 input_file_path,
                                                 mr_output_file_path)

        if debug:
            print(cmd)

        os.system(cmd)

        cmd = "mv {}.mr {}".format(mr_output_file_path, mr_output_file_path)
        os.system(cmd)

        # READ THE MR_TRANSFORM OUTPUT FILE ####################

        wavelet_planes = fits.load_fits_image(mr_output_file_path, 0)

        # CHECK RESULT #########################################

        if wavelet_planes.ndim != 3:
            msg = "Unexpected error: the output FITS file should contain a 3D array."
            raise WrongDimensionError(msg)

    finally:

        # REMOVE FITS FILES ####################################

        os.remove(input_file_path)
        os.remove(mr_output_file_path)

    wavelet_planes_list = [plane for plane in wavelet_planes]

    # INJECT NOISE IN NAN: PUT BACK NAN VALUES #############

    if noise_distribution is not None:
        for plane in wavelet_planes_list:
            plane[nan_mask] = np.nan

    return wavelet_planes_list


def inverse_wavelet_transform(wavelet_planes,
                              last_plane=DEFAULT_LAST_SCALE_TREATMENT):
    """Compute the inverse wavelet transform of `wavelet_planes`.

    Parameters
    ----------
    wavelet_planes : list of array_like
        The wavelet planes to (inverse) transform.
    last_plane : str, optional
        Define what to do with the last plane: 'keep' to keep it in the inverse
        transform, 'drop' to remove it in the inverse transform, 'mask' to keep
        only pixels that are *significant* in the others planes.

    Returns
    -------
    array_like
        Return the cleaned image.
    """
    output_image = np.zeros(wavelet_planes[0].shape)

    for plane in wavelet_planes[0:-1]:
        # Sum all planes except the last one (residuals plane)
        output_image += plane

    # Apply a special treatment with the last plane (residuals plane)
    if last_plane == "keep":

        # Keep the last plane
        output_image += wavelet_planes[-1]

    elif last_plane == "mask":

        # Only keep last plane's pixels that are *significant* in the others planes
        significant_pixels_mask = np.zeros(wavelet_planes[0].shape)
        for plane in wavelet_planes[0:-1]:
            significant_pixels_mask[plane != 0] = 1
        output_image += wavelet_planes[-1] * significant_pixels_mask

    return output_image
