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

__all__ = ['get_pixels_clusters',
           'filter_pixels_clusters',
           'filter_pixels_clusters_stats',
           'number_of_pixels_clusters']

import numpy as np
import scipy.ndimage as ndimage

"""Pixel clusters filtering.

Notes
-----
    Reference: https://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.ndimage.measurements.label.html
"""

def get_pixels_clusters(array, threshold=0):
    """Return pixels clusters in the given image ``array``.

    Parameters
    ----------
    array : array_like
        The input image where pixels clusters are searched. ``array`` should
        be a 2D Numpy array.
        A pixel cluster is a group of consecutive pixels having a value
        strictly greater than 0.
        Consecutive pixels are vertically or horizontally connected pixels,
        i.e. vertical or horizontal neighbors
        pixels; diagonal neighbors pixels are ignored.
    threshold : float
        A filtering is applied to the ``array`` image before pixels clusters
        are searched.
        All pixels strictly lower than ``threshold`` in ``array`` are set to 0.
        If ``threshold`` value is ``None`` or lower than 0 then ``threshold``
        is automatically set to 0 before the filtering is applied.

    Returns
    -------
    filtered_array : array_like
        The ``array`` image after the pre-processing filtering i.e. with all
        pixels below ``threshold`` put to 0 (may contain ``NaN`` values).

    label_array : array_like
        An integer Numpy array where each unique pixels cluster in ``input``
        has a unique ID.
        This array defines the pixels cluster ID each pixel belongs to
        This array never contains ``NaN`` values.

    num_clusters : int
        The number of pixels clusters in the ``array`` image.

    Examples
    --------

    Lets search pixels clusters in the following ``img`` image:

    >>> import numpy as np
    >>> img = np.array([[0, 0, 1, 3, 0, -1],
    ...                 [0, 0, 0, 5, 0,  0],
    ...                 [4, 3, 0, 0, 1,  0],
    ...                 [0, 0, 0, 8, 0,  0]])
    >>> filtered_array, label_array, num_clusters = get_pixels_clusters(img)

    The default filtering threshold is applied here;
    the top right pixel is put to 0 before pixels clusters are searched:

    >>> print(filtered_array)
    ... # doctest: +NORMALIZE_WHITESPACE
    [[ 0.  0.  1.  3.  0.  0.]
     [ 0.  0.  0.  5.  0.  0.]
     [ 4.  3.  0.  0.  1.  0.]
     [ 0.  0.  0.  8.  0.  0.]]

    This image contains 4 pixels clusters:

    >>> print(num_clusters)
    4

    Each of the 4 clusters are labeled with a different integer:

    >>> print(label_array)
    [[0 0 1 1 0 0]
     [0 0 0 1 0 0]
     [2 2 0 0 3 0]
     [0 0 0 4 0 0]]

    See Also
    --------
    scipy.ndimage.measurements.label
        The underlying function used for pixels clusters detection
        (https://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.ndimage.measurements.label.html)
    """

    if threshold is None:
        threshold = 0.

    array = array.astype('float64', copy=True)
    filtered_array = np.copy(array)

    # Put NaN pixels to 0
    # This is OK as long as it is made temporary and internally to avoid issues
    # with scipy
    filtered_array[np.isnan(filtered_array)] = 0.

    # Put to 0 pixels that are below 'threshold'
    filtered_array[filtered_array < threshold] = 0.
    mask = filtered_array > 0

    # Detect pixels clusters (named "label" in scipy)
    label_array, num_clusters = ndimage.label(mask) #, structure=np.ones((5, 5)))

    # Put back NaN in filtered_array (required to avoid bugs in others
    # functions e.g. incoherent dimensions with pixels_positions).
    filtered_array[np.isnan(array)] = np.nan

    return filtered_array, label_array, num_clusters


def filter_pixels_clusters(array, threshold=0):
    """Keep only pixels belonging to the largest cluster of pixels and put all others pixels to 0.

    Parameters
    ----------
    array : array_like
        The input image to filter. ``array`` should be a 2D Numpy array.
    threshold : float
        A filtering is applied to the ``array`` image before pixels clusters
        are searched.
        See ``get_pixels_clusters`` documentation for more details.

    Returns
    -------
    Numpy array
        The input image ``array`` where only pixels belonging to the largest
        cluster of pixels are kept and where all others pixels are put to 0.

    Examples
    --------

    Lets search pixels clusters in the following ``img`` image:

    >>> import numpy as np
    >>> img = np.array([[0, 0, 1, 3, 0, -1],
    ...                 [0, 0, 0, 5, 0,  0],
    ...                 [4, 3, 0, 0, 1,  0],
    ...                 [0, 0, 0, 8, 0,  0]])
    >>> filtered_array = filter_pixels_clusters(img)

    This image contains 4 pixels clusters.
    Only the biggest one is kept:

    >>> print(filtered_array)
    ... # doctest: +NORMALIZE_WHITESPACE
    [[ 0.  0.  1.  3.  0.  0.]
     [ 0.  0.  0.  5.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.]]

    Notes
    -----
        See ``get_pixels_clusters`` documentation for more details.

    See Also
    --------
    get_pixels_clusters
    """

    array = array.astype('float64', copy=True)
    filtered_array, label_array, num_clusters = get_pixels_clusters(array, threshold)

    # Put NaN pixels to -inf
    # This is OK as long as it is made temporary and internally to avoid issues
    # with scipy
    filtered_array[np.isnan(filtered_array)] = -float('inf')

    # Count the number of pixels for each island
    num_pixels_per_island = ndimage.sum(filtered_array, label_array, range(num_clusters + 1))

    # Only keep the biggest island
    mask_biggest_island = num_pixels_per_island < np.max(num_pixels_per_island)
    remove_pixel = mask_biggest_island[label_array]

    filtered_array[remove_pixel] = 0

    # Put back NaN in filtered_array (required to avoid bugs in others
    # functions (e.g. uncoherent dimensions with pixels_positions).
    filtered_array[np.isnan(array)] = np.nan

    return filtered_array


def filter_pixels_clusters_stats(array, threshold=0):
    """Return statistics about *pixels clusters* in the given image ``array``.

    Parameters
    ----------
    array : array_like
        The image to analyse.
    threshold : float
        A filtering is applied to the ``array`` image before pixels clusters
        are searched.
        See ``get_pixels_clusters`` documentation for more details.

    Returns
    -------
    delta_value : float
        The sum of pixels value removed if ``filter_pixels_clusters`` is applied
        on the image ``array``.

    delta_abs_value : float
        The sum of the absolute value of pixels removed if ``filter_pixels_clusters``
        is applied on the image ``array``.

    delta_num_pixels : int
        The number of pixel put to 0 if ``filter_pixels_clusters`` is applied
        on the image ``array``.

    Notes
    -----
        See ``get_pixels_clusters`` documentation for more details.

    Examples
    --------

    Lets check stats about pixels clusters in the following ``img`` image:

    >>> import numpy as np
    >>> img = np.array([[0, 0, 1, 3, 0, -1],
    ...                 [0, 0, 0, 5, 0,  0],
    ...                 [4, 3, 0, 0, 1,  0],
    ...                 [0, 0, 0, 8, 0,  0]])
    >>> delta_value, delta_abs_value, delta_num_pixels = filter_pixels_clusters_stats(img)

    After filtering, the sum of removed pixels is 15:

    >>> print(delta_value)
    15.0

    After filtering, the sum of the absolute values of removed pixels is 17:

    >>> print(delta_abs_value)
    17.0

    After filtering, 5 pixels have been put to 0:
    >>> print(delta_num_pixels)
    5

    See Also
    --------
    get_pixels_clusters
    """

    array = array.astype('float64', copy=True)
    filtered_array = filter_pixels_clusters(array, threshold=threshold)

    delta_value = np.nansum(array - filtered_array)
    delta_abs_value = np.nansum(np.abs(array - filtered_array))

    array[np.isfinite(array) & (array != 0)] = 1                              # May genereate warnings on NaN values
    filtered_array[np.isfinite(filtered_array) & (filtered_array != 0)] = 1   # May genereate warnings on NaN values

    delta_num_pixels = np.nansum(array - filtered_array)

    return float(delta_value), float(delta_abs_value), int(delta_num_pixels)


def number_of_pixels_clusters(array, threshold=0):
    """Return the number of *pixels clusters* in the given image ``array``.

    Parameters
    ----------
    array : array_like
        The image to analyse.
    threshold : float
        A filtering is applied to the ``array`` image before pixels clusters
        are searched.
        See ``get_pixels_clusters`` documentation for more details.

    Returns
    -------
    int
        The number of pixel clusters in the image ``array``.

    Examples
    --------

    Lets count pixels clusters in the following ``img`` image:

    >>> import numpy as np
    >>> img = np.array([[0, 0, 1, 3, 0, -1],
    ...                 [0, 0, 0, 5, 0,  0],
    ...                 [4, 3, 0, 0, 1,  0],
    ...                 [0, 0, 0, 8, 0,  0]])
    >>> num_clusters = number_of_pixels_clusters(img)

    This image contains 4 pixels clusters:

    >>> print(num_clusters)
    4

    Notes
    -----
        See ``get_pixels_clusters`` documentation for more details.

    See Also
    --------
    get_pixels_clusters
    """

    filtered_array, label_array, num_labels = get_pixels_clusters(array, threshold)
    return num_labels
