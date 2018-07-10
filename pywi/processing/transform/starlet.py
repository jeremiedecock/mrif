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

__all__ = ['StarletError',
           'WrongDimensionError',
           'wavelet_transform',
           'inverse_wavelet_transform']

"""Starlet Transform.

This module contains a "naive" (i.e. non-optimized) implementation of the 
Starlet transform.
"""

import numpy as np

from numba import jit

from pywi.io import images

# CONSTANTS ##################################################################

AVAILABLE_LAST_SCALE_OPTIONS = ('keep', 'drop', 'mask', 'posmask')
DEFAULT_LAST_SCALE_TREATMENT = 'mask'

# EXCEPTIONS #################################################################

class StarletError(Exception):
    """Common `starlet` module's error."""
    pass

class WrongDimensionError(StarletError):
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

@jit
def get_pixel_value(image, x, y, type_border):

    if type_border == 0:

        #try:
        pixel_value = image[x, y]
        return pixel_value
        #except IndexError as e:
        #    return 0

    elif type_border == 1:

        num_lines, num_col = image.shape    # TODO
        x = x % num_lines
        y = y % num_col
        pixel_value = image[x, y]
        return pixel_value

    elif type_border == 2:

        num_lines, num_col = image.shape    # TODO

        if x >= num_lines:
            x = num_lines - 2 - x
        elif x < 0:
            x = abs(x)

        if y >= num_col:
            y = num_col - 2 - y
        elif y < 0:
            y = abs(y)

        pixel_value = image[x, y]
        return pixel_value

    elif type_border == 3:

        num_lines, num_col = image.shape    # TODO

        if x >= num_lines:
            x = num_lines - 1 - x
        elif x < 0:
            x = abs(x) - 1

        if y >= num_col:
            y = num_col - 1 - y
        elif y < 0:
            y = abs(y) - 1

        pixel_value = image[x, y]
        return pixel_value

    else:
        raise ValueError()


@jit
def smooth_bspline(input_image, type_border, step_trou):
    """Apply a convolution kernel on the image using the "à trou" algorithm.

    Pseudo code:

    **convolve(scale, $s_i$):**

    $c_0 \leftarrow 3/8$

    $c_1 \leftarrow 1/4$

    $c_2 \leftarrow 1/16$

    $s \leftarrow \lfloor 2^{s_i} + 0.5 \rfloor$

    **for** all columns $x_i$

    $\quad$ **for** all rows $y_i$

    $\quad\quad$ scale[$x_i$, $y_i$] $\leftarrow$ $c_0$ . scale[$x_i$, $y_i$] + $c_1$ . scale[$x_i-s$, $y_i$] + $c_1$ . scale[$x_i+s$, $y_i$] + $c_2$ . scale[$x_i-2s$, $y_i$] + $c_2$ . scale[$x_i+2s$, $y_i$]

    **for** all columns $x_i$

    $\quad$ **for** all rows $y_i$

    $\quad\quad$ scale[$x_i$, $y_i$] $\leftarrow$ $c_0$ . scale[$x_i$, $y_i$] + $c_1$ . scale[$x_i$, $y_i-s$] + $c_1$ . scale[$x_i$, $y_i+s$] + $c_2$ . scale[$x_i$, $y_i-2s$] + $c_2$ . scale[$x_i$, $y_i+2s$]

    Inspired by Sparce2D mr_transform (originally implemented in *isap/cxx/sparse2d/src/libsparse2d/IM_Smooth.cc* in the
    *smooth_bspline()* function.

    ```cpp
    void smooth_bspline (const Ifloat & Im_in,
                         Ifloat &Im_out,
                         type_border Type, int Step_trou) {
        int Nl = Im_in.nl();  // num lines in the image
        int Nc = Im_in.nc();  // num columns in the image
        int i,j,Step;
        float Coeff_h0 = 3. / 8.;
        float Coeff_h1 = 1. / 4.;
        float Coeff_h2 = 1. / 16.;
        Ifloat Buff(Nl,Nc,"Buff smooth_bspline");

        Step = (int)(pow((double)2., (double) Step_trou) + 0.5);

        for (i = 0; i < Nl; i ++)
        for (j = 0; j < Nc; j ++)
           Buff(i,j) = Coeff_h0 *    Im_in(i,j)
                     + Coeff_h1 * (  Im_in (i, j-Step, Type)
                                   + Im_in (i, j+Step, Type))
                     + Coeff_h2 * (  Im_in (i, j-2*Step, Type)
                                   + Im_in (i, j+2*Step, Type));

        for (i = 0; i < Nl; i ++)
        for (j = 0; j < Nc; j ++)
           Im_out(i,j) = Coeff_h0 *    Buff(i,j)
                       + Coeff_h1 * (  Buff (i-Step, j, Type)
                                     + Buff (i+Step, j, Type))
                       + Coeff_h2 * (  Buff (i-2*Step, j, Type)
                                     + Buff (i+2*Step, j, Type));
    }
    ```

    Parameters
    ----------
    input_image
    type_border
    step_trou

    Returns
    -------

    """

    input_image = input_image.astype('float64', copy=True)

    coeff_h0 = 3. / 8.
    coeff_h1 = 1. / 4.
    coeff_h2 = 1. / 16.

    num_lines, num_col = input_image.shape    # TODO

    buff = np.zeros(input_image.shape, dtype='float64')
    img_out = np.zeros(input_image.shape, dtype='float64')

    step = int(pow(2., step_trou) + 0.5)

    for i in range(num_lines):
        for j in range(num_col):
            buff[i,j]  = coeff_h0 *    get_pixel_value(input_image, i, j,        type_border)
            buff[i,j] += coeff_h1 * (  get_pixel_value(input_image, i, j-step,   type_border) \
                                     + get_pixel_value(input_image, i, j+step,   type_border))
            buff[i,j] += coeff_h2 * (  get_pixel_value(input_image, i, j-2*step, type_border) \
                                     + get_pixel_value(input_image, i, j+2*step, type_border))

    for i in range(num_lines):
        for j in range(num_col):
            img_out[i,j]  = coeff_h0 *    get_pixel_value(buff, i,        j, type_border)
            img_out[i,j] += coeff_h1 * (  get_pixel_value(buff, i-step,   j, type_border) \
                                        + get_pixel_value(buff, i+step,   j, type_border))
            img_out[i,j] += coeff_h2 * (  get_pixel_value(buff, i-2*step, j, type_border) \
                                        + get_pixel_value(buff, i+2*step, j, type_border))

    return img_out


@jit
def wavelet_transform(input_image,
                      number_of_scales=4,
                      noise_distribution=None,
                      debug=False):
    """Compute the starlet transform of `input_image`.

    Pseudo code:

    **wavelet_transform(input_image, num_scales):**

    scales[0] $\leftarrow$ input_image

    **for** $i \in [0, \dots, \text{num_scales} - 2]$

    $\quad$ scales[$i + 1$] $\leftarrow$ convolve(scales[$i$], $i$)

    $\quad$ scales[$i$] $\leftarrow$ scales[$i$] - scales[$i + 1$]


    Inspired by Sparce2D mr_transform (originally implemented in *isap/cxx/sparse2d/src/libsparse2d/MR_Trans.cc*)

    ```cpp
    static void mr_transform (Ifloat &Image,
                              MultiResol &MR_Transf,
                              Bool EdgeLineTransform,
                              type_border Border,
                              Bool Details) {
        // [...]
        MR_Transf.band(0) = Image;
        for (s = 0; s < Nbr_Plan -1; s++) {
           smooth_bspline (MR_Transf.band(s),MR_Transf.band(s+1),Border,s);
           MR_Transf.band(s) -= MR_Transf.band(s+1);
        }
        // [...]
    }
    ```

    Parameters
    ----------
    input_image : array_like
        The input image to transform.
    number_of_scales : int, optional
        The number of scales used to transform `input_image` or in other words
        the number of wavelet planes returned.
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

    input_image = input_image.astype('float64', copy=True)

    if input_image.ndim != 2:
        msg = "The data should be a 2D array."
        raise WrongDimensionError(msg)

    # INJECT NOISE IN NAN PIXELS ###########################################

    # TODO: should this noise injection be done in the abstract 'run()' function ?

    nan_mask = images.fill_nan_pixels(input_image, noise_distribution)

    # DO THE WAVELET TRANSFORM #############################################

    wavelet_planes_list = []
    wavelet_planes_list.append(input_image)

    for scale_index in range(number_of_scales - 1):
        previous_scale = wavelet_planes_list[scale_index]

        next_scale = smooth_bspline(previous_scale, 3, scale_index)

        previous_scale -= next_scale

        wavelet_planes_list.append(next_scale)

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

    elif last_plane == "posmask":

        # Only keep last plane's pixels that are *significant* with a *positive coefficient* in the others planes
        significant_pixels_mask = np.zeros(wavelet_planes[0].shape)
        for plane in wavelet_planes[0:-1]:
            significant_pixels_mask[plane > 0] = 1
        output_image += wavelet_planes[-1] * significant_pixels_mask

    return output_image
