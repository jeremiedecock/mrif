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

__all__ = ['filter_planes']

"""Filter images with .

TODO
"""

import copy
import numpy as np

from pywi.io import images
from pywi.processing.filtering.pixel_clusters import filter_pixels_clusters

# CONSTANTS ##################################################################

DEBUG = False                 # TODO: use sys flag
AVAILABLE_TYPE_OF_FILTERING = ('hard_filtering', 'cluster_filtering', 'ksigma_hard_filtering', 'common_hard_filtering')
DEFAULT_TYPE_OF_FILTERING = 'hard_filtering'
DEFAULT_FILTER_THRESHOLDS_STR = '0,0'            # TODO: change the default value...
DEFAULT_FILTER_THRESHOLDS = [float(threshold_str) for threshold_str in DEFAULT_FILTER_THRESHOLDS_STR.split(",")]

##############################################################################

def filter_planes(wavelet_planes,
                  method=DEFAULT_TYPE_OF_FILTERING,
                  thresholds=DEFAULT_FILTER_THRESHOLDS,
                  detect_only_positive_structures=False):
    """Filter the wavelet planes.

    The last plane (called residuals) is kept unmodified.
    
    Parameters
    ----------
    wavelet_planes : list of array_like
        The wavelet planes to filter, including the last *residual* plane.
    method : str, optional
        The filtering method to use. So far, only the 'hard_filtering' and
        'ksigma_hard_filtering' methods are implemented.
    thresholds : list of float
        Thresholds used for the plane filtering.
    detect_only_positive_structures : bool
        Detect only positive structures.

    Returns
    -------
    list
        Return a list containing the filtered wavelet planes.
    """
    filtered_wavelet_planes = copy.deepcopy(wavelet_planes)

    # The last plane is kept unmodified

    for plane_index, plane in enumerate(wavelet_planes[0:-1]):

        if method in ('hard_filtering', 'common_hard_filtering'):

            with np.errstate(invalid='ignore'):      # TODO: to disable warnings on images containing "NaN" values (temporary solution)
                if detect_only_positive_structures:
                    plane_mask = plane > thresholds[plane_index]
                else:
                    plane_mask = abs(plane) > thresholds[plane_index]

            filtered_plane = plane * plane_mask

        elif method == 'ksigma_hard_filtering':

            # Compute the standard deviation of the plane ##

            plane_noise_std = np.std(plane)  # TODO: this is wrong... it should be the estimated std of the **noise**

            # Apply a threshold on the plane ###############

            # Remark: "abs(plane) > (plane_noise_std * 3.)" should be the correct way to
            # make the image mask, but sometimes results looks better when all
            # negative coefficients are dropped ("plane > (plane_noise_std * 3.)")

            if detect_only_positive_structures:
                plane_mask = plane > (plane_noise_std * thresholds[plane_index])
            else:
                plane_mask = abs(plane) > (plane_noise_std * thresholds[plane_index])  

            filtered_plane = plane * plane_mask

        elif method == 'cluster_filtering':

            filtered_plane = filter_pixels_clusters(plane, threshold=thresholds[plane_index])

        else:

            raise ValueError('Unknown method "{}". Should be "hard_filtering" or "ksigma_hard_filtering".'.format(method))

        filtered_wavelet_planes[plane_index] = filtered_plane

        if DEBUG:
            images.plot(plane, title="Plane {}".format(plane_index))
            images.plot(plane_mask, title="Binary mask for plane {}".format(plane_index))
            images.plot(filtered_plane, title="Filtered plane {}".format(plane_index))

    if method == 'common_hard_filtering':

        # Use the same significant pixels on each plane

        # Init the common pixel mask to "all pixels rejected"
        common_significant_pixels_mask = np.zeros(wavelet_planes[0].shape)

        for filtered_plane in filtered_wavelet_planes[0:-1]:
            current_significant_pixels_mask = (np.isfinite(filtered_plane) * (filtered_plane != 0))
            common_significant_pixels_mask = np.logical_or(common_significant_pixels_mask, current_significant_pixels_mask)

        for plane_index, plane in enumerate(wavelet_planes[0:-1]):
            filtered_plane = plane * common_significant_pixels_mask
            filtered_wavelet_planes[plane_index] = filtered_plane

    return filtered_wavelet_planes
