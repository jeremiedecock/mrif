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

"""Denoise FITS images with Wavelet Transform.

This script use mr_filter -- a program written CEA/CosmoStat
(www.cosmostat.org) -- to make Wavelet Transform.

Notes
-----
This script requires the mr_filter program
(http://www.cosmostat.org/software/isap/).
"""

__all__ = ['WaveletTransform']

import numpy as np
import os
import time

from pywi.processing.filtering.pixel_clusters import filter_pixels_clusters as scipy_kill_isolated_pixels
from pywi.processing.filtering.pixel_clusters import filter_pixels_clusters_stats
from pywi.processing.filtering.pixel_clusters import number_of_pixels_clusters

from pywi.io import images
from pywi.io import fits

# CONSTANTS ##################################################################

DEBUG = False

# EXCEPTIONS #################################################################

class MrFilterError(Exception):
    pass

class WrongDimensionError(MrFilterError):
    """Exception raised when trying to save a FITS with more than 3 dimensions
    or less than 2 dimensions.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self):
        super(WrongDimensionError, self).__init__("Unexpected error: the output FITS file should contain a 2D array.")


##############################################################################

def clean_image(input_img,
                type_of_multiresolution_transform=None,
                type_of_filters=None,
                type_of_non_orthog_filters=None,
                number_of_scales=None,
                suppress_last_scale=False,
                suppress_isolated_pixels=False,
                kill_isolated_pixels=False,
                coef_detection_method=None,
                k_sigma_noise_threshold=None,
                noise_model=None,
                detect_only_positive_structure=False,
                suppress_positivity_constraint=False,
                type_of_filtering=None,
                first_detection_scale=None,
                number_of_iterations=None,
                epsilon=None,
                support_file_name=None,
                precision=None,
                mask_file_path=None,
                offset_after_calibration=None,
                correction_offset=False,
                input_image_scale='linear',
                noise_distribution=None,
                verbose=False,
                raw_option_string=None,
                tmp_files_directory=".",       # "/Volumes/ramdisk"
                mrfilter_directory=None,       # "/Volumes/ramdisk"
                output_data_dict=None,
                **kwargs):
    """Clean the `input_img` image.

    Apply the wavelet transform, filter planes and return the reverse
    transformed image.

    Parameters
    ----------
    input_img : array_like
        The input image to transform.
    number_of_scales : int
        The number of scales used to transform `input_image` or in other words
        the number of wavelet planes returned.
    tmp_files_directory : str
        The path of the directory used to store mr_transform temporary data.
        The default is the current directory, but it may be more appropriate to
        specify here the path of a directory mounted in a ramdisk to speedup
        I/Os ("/Volumes/ramdisk" on MacOSX or "/dev/shm" on Linux).
    noise_distribution : EmpiricalDistribution
        The noise distribution used to fill 'empty' NaN pixels with the
        appropriate random noise distribution. If none, NaN pixels are fill
        with zeros (which may add unwanted harmonics in wavelet planes).

    Returns
    -------
    array_like
        Return the cleaned image.

    Raises
    ------
    WrongDimensionError
        If `cleaned_img` is not a 2D array.
    """

    input_img = input_img.copy()

    if input_img.ndim != 2:
        raise WrongDimensionError()

    input_file_path = os.path.join(tmp_files_directory, ".tmp_{}_{}_in.fits".format(os.getpid(), time.time()))
    mr_output_file_path = os.path.join(tmp_files_directory, ".tmp_{}_{}_out.fits".format(os.getpid(), time.time()))

    if output_data_dict is not None:
        output_data_dict["mr_input_tmp_file_path"] = input_file_path
        output_data_dict["mr_output_tmp_file_path"] = mr_output_file_path

    if (output_data_dict is not None) and (mask_file_path is not None):
        output_data_dict["mr_mask_file_path"] = mask_file_path

    # INJECT NOISE IN NAN ##################################

    # See https://stackoverflow.com/questions/29365194/replacing-missing-values-with-random-in-a-numpy-array

    nan_mask = images.fill_nan_pixels(input_img, noise_distribution)

    # APPLY AN OFFSET ######################################

    if offset_after_calibration is not None:
        if verbose:
            print("Apply an offset after calibration:", offset_after_calibration)
        input_img = input_img + offset_after_calibration

    # CHANGE THE SCALE #####################################

    if input_image_scale == 'log':
        if verbose:
            print("Apply log scale")
        #images.plot(input_img)
        input_img = np.log10(input_img)  # TODO: it creates NaN values where pixels <= 0
        #images.plot(input_img)
    elif input_image_scale == 'sqrt':
        if verbose:
            print("Apply sqrt scale")
        #images.plot(input_img)
        input_img = np.sqrt(input_img)   # TODO: it creates NaN values where pixels < 0
        #images.plot(input_img)

    # WRITE THE INPUT FILE (FITS) ##########################

    try:
        initial_time = time.perf_counter()
        fits.save_fits_image(input_img, input_file_path)
        exec_time_sec = time.perf_counter() - initial_time
        if output_data_dict is not None:
            output_data_dict["save_tmp_file_time_sec"] = exec_time_sec
    except:
        print("Error on input FITS file:", input_file_path)
        raise

    # EXECUTE MR_FILTER ####################################

    # TODO: improve the following lines
    if mrfilter_directory is None:
        cmd = 'mr_filter'
    else:
        cmd = os.path.join(mrfilter_directory, 'mr_filter')

    if raw_option_string is None:
        cmd += ' -t{}'.format(type_of_multiresolution_transform) if type_of_multiresolution_transform is not None else ''
        cmd += ' -T{}'.format(type_of_filters) if type_of_filters is not None else ''
        cmd += ' -U{}'.format(type_of_non_orthog_filters) if type_of_non_orthog_filters is not None else ''
        cmd += ' -n{}'.format(number_of_scales) if number_of_scales is not None else ''
        cmd += ' -K' if suppress_last_scale else ''
        cmd += ' -k' if suppress_isolated_pixels else ''      # You should use scipy implementation instead (pywi/denoising/filter_pixels_clusters.py); it's much more efficient
        cmd += ' -C{}'.format(coef_detection_method) if coef_detection_method is not None else ''
        cmd += ' -s{}'.format(k_sigma_noise_threshold) if k_sigma_noise_threshold is not None else ''
        cmd += ' -m{}'.format(noise_model) if noise_model is not None else ''
        cmd += ' -p' if detect_only_positive_structure else ''
        cmd += ' -P' if suppress_positivity_constraint else ''
        cmd += ' -f{}'.format(type_of_filtering) if type_of_filtering is not None else ''
        cmd += ' -F{}'.format(first_detection_scale) if first_detection_scale is not None else ''
        cmd += ' -i{}'.format(number_of_iterations) if number_of_iterations is not None else ''
        cmd += ' -e{}'.format(epsilon) if epsilon is not None else ''
        cmd += ' -w{}'.format(support_file_name) if support_file_name is not None else ''
        cmd += ' -E{}'.format(precision) if precision is not None else ''
        cmd += ' -I {}'.format(mask_file_path) if mask_file_path is not None else ''

        cmd += ' -v' if verbose else ''
    else:
        cmd += ' ' + raw_option_string

    cmd += ' "{}" "{}"'.format(input_file_path, mr_output_file_path)

    #cmd = 'mr_filter -K -k -C1 -s3 -m3 -n{} "{}" {}'.format(number_of_scales, input_file_path, mr_output_file_path)
    #cmd = 'mr_filter -K -k -C1 -s3 -m2 -p -P -n{} "{}" {}'.format(number_of_scales, input_file_path, mr_output_file_path)

    if verbose:
        print()
        print(cmd)
    else:
        cmd += ' > /dev/null'

    try:
        initial_time = time.perf_counter()
        os.system(cmd)
        exec_time_sec = time.perf_counter() - initial_time
        if output_data_dict is not None:
            output_data_dict["mrfilter_cmd_exec_time_sec"] = exec_time_sec
    except:
        print("Error on command:", cmd)
        raise

    # READ THE MR_FILTER OUTPUT FILE #######################

    try:
        initial_time = time.perf_counter()
        cleaned_img = fits.load_fits_image(mr_output_file_path, 0)
        exec_time_sec = time.perf_counter() - initial_time
        if output_data_dict is not None:
            output_data_dict["load_tmp_file_time_sec"] = exec_time_sec
    except:
        print("Error on output FITS file:", mr_output_file_path)
        raise

    # REMOVE FITS FILES ####################################

    os.remove(input_file_path)
    os.remove(mr_output_file_path)

    # CHECK RESULT #########################################

    if cleaned_img.ndim != 2:
        raise WrongDimensionError()

    # INJECT NOISE IN NAN: PUT BACK NAN VALUES #############

    cleaned_img[nan_mask] = np.nan

    # CHANGE THE SCALE #####################################

    if input_image_scale == 'log':
        if verbose:
            print("Invert log scale")
        cleaned_img = np.power(10., cleaned_img)
    elif input_image_scale == 'sqrt':
        if verbose:
            print("Invert sqrt scale")
        cleaned_img = np.power(2., cleaned_img)

    # INVERT THE OFFSET ####################################

    if (offset_after_calibration is not None) and (not suppress_last_scale):
        cleaned_img = cleaned_img - offset_after_calibration

    # CORRECTION OFFSET ####################################

    if correction_offset:
        if verbose:
            print("Apply a correction offset after cleaning")
        cleaned_img = cleaned_img - np.nanmin(cleaned_img)
        cleaned_img[ np.isfinite(cleaned_img) & (cleaned_img < 1.0) ] = 0.   # May genereate warnings on NaN values

    # KILL ISOLATED PIXELS #################################

    img_cleaned_islands_delta_pe, img_cleaned_islands_delta_abs_pe, img_cleaned_islands_delta_num_pixels = filter_pixels_clusters_stats(cleaned_img)
    img_cleaned_num_islands = number_of_pixels_clusters(cleaned_img)

    if output_data_dict is not None:
        output_data_dict["img_cleaned_islands_delta_pe"] = img_cleaned_islands_delta_pe
        output_data_dict["img_cleaned_islands_delta_abs_pe"] = img_cleaned_islands_delta_abs_pe
        output_data_dict["img_cleaned_islands_delta_num_pixels"] = img_cleaned_islands_delta_num_pixels
        output_data_dict["img_cleaned_num_islands"] = img_cleaned_num_islands

    if kill_isolated_pixels:
        if verbose:
            print("Kill isolated pixels")
        initial_time = time.perf_counter()
        cleaned_img = scipy_kill_isolated_pixels(cleaned_img)
        exec_time_sec = time.perf_counter() - initial_time
        if output_data_dict is not None:
            output_data_dict["scipy_kill_isolated_pixels_time_sec"] = exec_time_sec

    #print(cleaned_img)
    #images.plot_hist(cleaned_img)
    #images.plot_hist(cleaned_img, num_bins=500, x_max=5)

    return cleaned_img
