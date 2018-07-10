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

__all__ = ['clean_image']

"""Denoise images with Starlet.

TODO...
"""

from pywi.processing.filtering import hard_filter
from pywi.processing.filtering.hard_filter import filter_planes
from pywi.processing.filtering.pixel_clusters import filter_pixels_clusters
from pywi.processing.filtering.pixel_clusters import filter_pixels_clusters_stats
from pywi.processing.filtering.pixel_clusters import number_of_pixels_clusters
from pywi.processing.transform import starlet
from pywi.processing.transform.starlet import wavelet_transform
from pywi.processing.transform.starlet import inverse_wavelet_transform

from pywi.io import images

# CONSTANTS ##################################################################

DEBUG = False

##############################################################################

def clean_image(input_image,
                type_of_filtering=hard_filter.DEFAULT_TYPE_OF_FILTERING,
                filter_thresholds=hard_filter.DEFAULT_FILTER_THRESHOLDS,
                last_scale_treatment=starlet.DEFAULT_LAST_SCALE_TREATMENT,
                detect_only_positive_structures=False,
                kill_isolated_pixels=False,
                noise_distribution=None,
                output_data_dict=None,
                **kwargs):
    """Clean the `input_image` image.

    Apply the wavelet transform, filter planes and return the reverse
    transformed image.

    Parameters
    ----------
    input_image : array_like
        The image to clean.
    type_of_filtering : str
        Type of filtering: 'hard_filtering' or 'ksigma_hard_filtering'.
    filter_thresholds : list of float
        Thresholds used for the plane filtering.
    last_scale_treatment : str
        Last plane treatment: 'keep', 'drop' or 'mask'.
    detect_only_positive_structures : bool
        Detect only positive structures.
    kill_isolated_pixels : bool
        Suppress isolated pixels in the support. It assumes a uniform background.
    noise_distribution : bool
        The JSON file containing the Cumulated Distribution Function of the
        noise model used to inject artificial noise in blank pixels (those
        with a NaN value).
    output_data_dict : dict
        A dictionary used to return results and intermediate results.

    Returns
    -------
        Return the cleaned image.
    """

    if DEBUG:
        print("Filter thresholds:", filter_thresholds)

    number_of_scales = len(filter_thresholds) + 1

    if DEBUG:
        print("Number of scales:", number_of_scales)

    # COMPUTE THE WAVELET TRANSFORM #######################################

    wavelet_planes = wavelet_transform(input_image,
                                       number_of_scales=number_of_scales,
                                       noise_distribution=noise_distribution)

    if DEBUG:
        for index, plane in enumerate(wavelet_planes):
            images.plot(plane, "Plane " + str(index))

    # FILTER WAVELET PLANES ###############################################

    filtered_wavelet_planes = filter_planes(wavelet_planes,
                                            method=type_of_filtering,
                                            thresholds=filter_thresholds,
                                            detect_only_positive_structures=detect_only_positive_structures)

    if DEBUG:
        for index, plane in enumerate(filtered_wavelet_planes):
            images.plot(plane, "Filtered plane " + str(index))

    # COMPUTE THE INVERSE TRANSFORM #######################################

    cleaned_image = inverse_wavelet_transform(filtered_wavelet_planes,
                                              last_plane=last_scale_treatment)
    if DEBUG:
        images.plot(cleaned_image, "Cleaned image")

    # REMOVE ISOLATED PIXELS ##############################################

    if output_data_dict is not None:
        # TODO: drop this ?
        img_cleaned_clusters_delta_intensity, img_cleaned_clusters_delta_abs_intensity, img_cleaned_clusters_delta_num_pixels = filter_pixels_clusters_stats(cleaned_image)
        img_cleaned_num_islands = number_of_pixels_clusters(cleaned_image)

        output_data_dict["img_cleaned_clusters_delta_intensity"] = img_cleaned_clusters_delta_intensity
        output_data_dict["img_cleaned_clusters_delta_abs_intensity"] = img_cleaned_clusters_delta_abs_intensity
        output_data_dict["img_cleaned_clusters_delta_num_pixels"] = img_cleaned_clusters_delta_num_pixels
        output_data_dict["img_cleaned_num_islands"] = img_cleaned_num_islands

    if kill_isolated_pixels:
        cleaned_image = filter_pixels_clusters(cleaned_image)
        if DEBUG:
            images.plot(cleaned_image, "Cleaned image after cluster filtering")

    return cleaned_image
