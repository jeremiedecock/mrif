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

__all__ = ['normalize_array',
           'mse',
           'nrmse',
           #'number_of_clusters',
           #'metric1',
           #'metric2',
           #'metric3',
           #'metric4',
           'psnr',
           'ssim']

import numpy as np

#from pywi.image.pixel_clusters import filter_pixels_clusters_stats

from skimage.measure import compare_ssim as ski_ssim
from skimage.measure import compare_psnr as ski_psnr
#from skimage.measure import compare_nrmse as ski_nrmse

###############################################################################
# EXCEPTIONS                                                                  #
###############################################################################

class RefBasedMetricError(Exception):
    """Exceptions common to the pywi.benchmark.metrics.refbased module"""
    pass

class EmptyOutputImageError(RefBasedMetricError):
    """Exception raised when the output image only have null pixels"""

    def __init__(self):
        super(EmptyOutputImageError, self).__init__("Empty output image error")

class EmptyReferenceImageError(RefBasedMetricError):
    """Exception raised when the reference image only have null pixels"""

    def __init__(self):
        super(EmptyReferenceImageError, self).__init__("Empty reference image error")


###############################################################################
# TOOL FUNCTIONS                                                              #
###############################################################################

def normalize_array(array):
    r"""Normalize the given array such that its values fit between 0.0
    and 1.0.

    It applies

    .. math::

        \text{normalize}(\boldsymbol{S}) = \frac{ \boldsymbol{S} - \text{min}(\boldsymbol{S}) }{ \text{max}(\boldsymbol{S}) - \text{min}(\boldsymbol{S}) }

    where :math:`\boldsymbol{S}` is the input array (an image).

    Parameters
    ----------
    image : Numpy array
        The image to normalize (whatever its shape)

    Returns
    -------
    Numpy array
        The normalized version of the input image (keeping the same dimension
        and shape)
    """

    # Copy and cast images to prevent tricky bugs
    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
    input_array = array.astype('float64', copy=True)

    min_value = np.nanmin(input_array)
    max_value = np.nanmax(input_array)

    output_array = (input_array - min_value) / float(max_value - min_value)

    return output_array


###############################################################################
# METRIC FUNCTIONS                                                            #
###############################################################################

# Mean-Squared Error (MSE) ####################################################

def mse(image, reference_image):
    r"""Compute the score of ``image`` regarding ``reference_image``
    with the *Mean-Squared Error* (MSE) metric.

    It applies

    .. math::

        \text{MSE}(\hat{\boldsymbol{S}}, \boldsymbol{S}^*) = \left\langle \left( \hat{\boldsymbol{S}} - \boldsymbol{S}^* \right)^{\circ 2} \right\rangle

    with:
    
    - :math:`\hat{\boldsymbol{S}}` the algorithm's output image (i.e. the
      *cleaned* image);
    - :math:`\boldsymbol{S}^*` the reference image (i.e. the *clean* image);
    - :math:`\langle \boldsymbol{S} \rangle` the average of matrix
      :math:`\boldsymbol{S}`;
    - :math:`\boldsymbol{S}^{\circ 2}` the
      `Hadamar power <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#Analogous_operations>`_
      (i.e. the element wise square) of matrix :math:`\boldsymbol{S}`.

    See http://scikit-image.org/docs/dev/api/skimage.measure.html#compare-mse
    for more information.

    Note
    ----
    This function is not well-suited to high dynamic range images handled with
    this project (errors are correlated with energy levels).

    Parameters
    ----------
    image: 2D ndarray
        The cleaned image returned by the image cleanning algorithm to assess.
    reference_image: 2D ndarray
        The actual clean image (the best result that can be expected for the
        image cleaning algorithm).

    Returns
    -------
    float
        The score of the image cleaning algorithm for the given image.

    
    """

    # Copy and cast images to prevent tricky bugs
    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
    image = image.astype('float64', copy=True)
    reference_image = reference_image.astype('float64', copy=True)
    
    score = np.nanmean(np.square(image - reference_image))

    return float(score)


# Normalized Root Mean-Squared Error (NRMSE) ##################################

def nrmse(image, reference_image):
    r"""Compute the score of ``image`` regarding ``reference_image``
    with the *Normalized Root Mean-Squared Error* (NRMSE) metric.

    It applies

    .. math::

        \text{NRMSE}(\hat{\boldsymbol{S}}, \boldsymbol{S}^*) = \frac{\sqrt{\text{MSE}}}{\sqrt{ \left\langle \hat{\boldsymbol{S}} \circ \boldsymbol{S}^* \right\rangle }}

    with:
    
    - :math:`\hat{\boldsymbol{S}}` the algorithm's output image (i.e. the
      *cleaned* image);
    - :math:`\boldsymbol{S}^*` the reference image (i.e. the *clean* image);
    - :math:`\langle \boldsymbol{S} \rangle` the average of matrix
      :math:`\boldsymbol{S}`;
    - :math:`\circ` the
      `Hadamar product <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)>`_
      (i.e. the element wise product operator).

    See http://scikit-image.org/docs/dev/api/skimage.measure.html#compare-nrmse and
    https://en.wikipedia.org/wiki/Root-mean-square_deviation for more information.

    Parameters
    ----------
    image: 2D ndarray
        The cleaned image returned by the image cleanning algorithm to assess.
    reference_image: 2D ndarray
        The actual clean image (the best result that can be expected for the
        image cleaning algorithm).

    Returns
    -------
    float
        The score of the image cleaning algorithm for the given image.

    
    """

    # Copy and cast images to prevent tricky bugs
    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
    image = image.astype('float64', copy=True)
    reference_image = reference_image.astype('float64', copy=True)
    
    #if ('nrmse_normalize_type' in kwargs) and (kwargs['nrmse_normalize_type'].lower() == 'euclidian'):
    #    denom = 
    # TODO: see https://github.com/scikit-image/scikit-image/blob/master/skimage/measure/simple_metrics.py#L82

    _mse = mse(image, reference_image)
    denom = np.sqrt(np.nanmean((reference_image * image), dtype=np.float64))

    if denom == 0:
        score = float('nan')
    else:
        score = float(np.sqrt(_mse) / denom)

    return score


## Unusual Normalized Root Mean-Squared Error (uNRMSE) #########################
#
#def metric1(image, reference_image):
#    r"""Compute the score of ``image`` regarding ``reference_image``
#    with a (unusually) normalized version of the *Root Mean-Squared Error*
#    (RMSE) metric.
#
#    It applies
#
#    .. math::
#
#        \text{uNRMSE}(\hat{\boldsymbol{S}}, \boldsymbol{S}^*) = \left\langle \left( \left( \hat{\boldsymbol{S}}_n - \boldsymbol{S}^*_n \right)^{\circ 2} \right)^{\circ \frac{1}{2}} \right\rangle
#
#    with:
#    
#    - :math:`\hat{\boldsymbol{S}}_n`
#      the algorithm's normalized output image (i.e. the *cleaned* image),
#      (using :func:`normalize_array`);
#    - :math:`\boldsymbol{S}^*_n`
#      the normalized reference image (i.e. the *clean* image)
#      (using :func:`normalize_array`);
#    - :math:`\langle \boldsymbol{S} \rangle` the average of matrix
#      :math:`\boldsymbol{S}`;
#    - :math:`\boldsymbol{S}^{\circ 2}` the
#      `Hadamar power <https://en.wikipedia.org/wiki/Hadamard_product_(matrices)#Analogous_operations>`_
#      (i.e. the element wise square) of matrix :math:`\boldsymbol{S}`.
#
#    Note
#    ----
#    This function is not robust to noise on extreme values.
#
#    Parameters
#    ----------
#    image: 2D ndarray
#        The cleaned image returned by the image cleanning algorithm to assess.
#    reference_image: 2D ndarray
#        The actual clean image (the best result that can be expected for the
#        image cleaning algorithm).
#
#    Returns
#    -------
#    float
#        The score of the image cleaning algorithm for the given image.
#
#    
#    """
#
#    # Copy and cast images to prevent tricky bugs
#    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
#    image = image.astype('float64', copy=True)
#    reference_image = reference_image.astype('float64', copy=True)
#    
#    image = normalize_array(image)
#    reference_image = normalize_array(reference_image)
#
#    score = np.nanmean(np.square(image - reference_image))
#
#    return float(score)
#
#
## Mean Pixel Difference 2 #####################################################
#
#def metric2(image, reference_image):
#    r"""Compute the score of ``image`` regarding ``reference_image``
#    with the :math:`\mathcal{E}_{\text{shape}}` metric.
#
#    It applies
#
#    .. math::
#
#        f(\hat{\boldsymbol{S}}, \boldsymbol{S}^*) = \left\langle \text{abs} \left( \frac{\hat{\boldsymbol{S}}}{\sum_i \hat{\boldsymbol{S}}_i} - \frac{\boldsymbol{S}^*}{\sum_i \boldsymbol{S}^*_i} \right) \right\rangle
#
#    with:
#    
#    - :math:`\hat{\boldsymbol{S}}` the algorithm's output image
#      (i.e. the *cleaned* image);
#    - :math:`\boldsymbol{S}^*` the reference image (i.e. the *clean* image);
#    - :math:`\langle \boldsymbol{S} \rangle` the average of matrix
#      :math:`\boldsymbol{S}`.
#
#    Parameters
#    ----------
#    image: 2D ndarray
#        The cleaned image returned by the image cleanning algorithm to assess.
#    reference_image: 2D ndarray
#        The actual clean image (the best result that can be expected for the
#        image cleaning algorithm).
#
#    Returns
#    -------
#    float
#        The score of the image cleaning algorithm for the given image.
#    """
#
#    # Copy and cast images to prevent tricky bugs
#    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
#    image = image.astype('float64', copy=True)
#    reference_image = reference_image.astype('float64', copy=True)
#    
#    sum_output_image = float(np.nansum(image))
#    sum_reference_image = float(np.nansum(reference_image))
#
#    if sum_output_image <= 0:                 # TODO
#        raise EmptyOutputImageError()
#
#    if sum_reference_image <= 0:              # TODO
#        raise EmptyReferenceImageError()
#
#    mark = np.nanmean(np.abs((image / sum_output_image) - (reference_image / sum_reference_image)))
#
#    return float(mark)
#
#
## Relative Total Counts Difference (mpdspd) ###################################
#
#def metric3(image, reference_image):
#    r"""Compute the score of ``image`` regarding ``reference_image``
#    with the :math:`\mathcal{E}^+_{\text{energy}}`
#    (a.k.a. *relative total counts difference*) metric.
#
#    It applies
#
#    .. math::
#
#        f(\hat{\boldsymbol{S}}, \boldsymbol{S}^*) = \frac{ \text{abs} \left( \sum_i \hat{\boldsymbol{S}}_i - \sum_i \boldsymbol{S}^*_i \right) }{ \sum_i \boldsymbol{S}^*_i }
#
#    with :math:`\hat{\boldsymbol{S}}` the algorithm's output image
#    (i.e. the *cleaned* image)
#    and :math:`\boldsymbol{S}^*` the reference image
#    (i.e. the *clean* image).
#
#    Parameters
#    ----------
#    image: 2D ndarray
#        The cleaned image returned by the image cleanning algorithm to assess.
#    reference_image: 2D ndarray
#        The actual clean image (the best result that can be expected for the
#        image cleaning algorithm).
#
#    Returns
#    -------
#    float
#        The score of the image cleaning algorithm for the given image.
#    """
#
#    # Copy and cast images to prevent tricky bugs
#    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
#    image = image.astype('float64', copy=True)
#    reference_image = reference_image.astype('float64', copy=True)
#    
#    sum_output_image = float(np.nansum(image))
#    sum_reference_image = float(np.nansum(reference_image))
#
#    if sum_reference_image <= 0:              # TODO
#        raise EmptyReferenceImageError()
#
#    mark = np.abs(sum_output_image - sum_reference_image) / sum_reference_image
#
#    return float(mark)
#
#
## Signed Relative Total Counts Difference (sspd) ##############################
#
#def metric4(image, reference_image):
#    r"""Compute the score of ``image`` regarding ``reference_image``
#    with the :math:`\mathcal{E}_{\text{energy}}`
#    (a.k.a. *signed relative total counts difference*) metric.
#    
#    It applies
#
#    .. math::
#
#        f(\hat{\boldsymbol{S}}, \boldsymbol{S}^*) = \frac{ \sum_i \hat{\boldsymbol{S}}_i - \sum_i \boldsymbol{S}^*_i }{ \sum_i \boldsymbol{S}^*_i }
#
#    with :math:`\hat{\boldsymbol{S}}` the algorithm's output image
#    (i.e. the *cleaned* image)
#    and :math:`\boldsymbol{S}^*` the reference image
#    (i.e. the *clean* image).
#
#    Parameters
#    ----------
#    image: 2D ndarray
#        The cleaned image returned by the image cleanning algorithm to assess.
#    reference_image: 2D ndarray
#        The actual clean image (the best result that can be expected for the
#        image cleaning algorithm).
#
#    Returns
#    -------
#    float
#        The score of the image cleaning algorithm for the given image.
#    """
#
#    # Copy and cast images to prevent tricky bugs
#    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
#    image = image.astype('float64', copy=True)
#    reference_image = reference_image.astype('float64', copy=True)
#    
#    sum_output_image = float(np.nansum(image))
#    sum_reference_image = float(np.nansum(reference_image))
#
#    if sum_reference_image <= 0:              # TODO
#        raise EmptyReferenceImageError()
#
#    mark = (sum_output_image - sum_reference_image) / sum_reference_image
#
#    return float(mark)


# Structural Similarity Index Measure (SSIM) ##################################

def ssim(image, reference_image):
    r"""Compute the score of ``image`` regarding ``reference_image``
    with the *Structural Similarity Index Measure* (SSIM) metric.

    See [1]_, [2]_, [3]_ and [4]_ for more information.
    
    The SSIM index is calculated on various windows of an image.
    The measure between two windows :math:`x` and :math:`y` of common size
    :math:`N.N` is:

    .. math::
        \hbox{SSIM}(x,y) = \frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}

    with:

    * :math:`\scriptstyle\mu_x` the average of :math:`\scriptstyle x`;
    * :math:`\scriptstyle\mu_y` the average of :math:`\scriptstyle y`;
    * :math:`\scriptstyle\sigma_x^2` the variance of :math:`\scriptstyle x`;
    * :math:`\scriptstyle\sigma_y^2` the variance of :math:`\scriptstyle y`;
    * :math:`\scriptstyle \sigma_{xy}` the covariance of :math:`\scriptstyle x` and :math:`\scriptstyle y`;
    * :math:`\scriptstyle c_1 = (k_1L)^2`, :math:`\scriptstyle c_2 = (k_2L)^2` two variables to stabilize the division with weak denominator;
    * :math:`\scriptstyle L` the dynamic range of the pixel-values (typically this is :math:`\scriptstyle 2^{\#bits\ per\ pixel}-1`);
    * :math:`\scriptstyle k_1 = 0.01` and :math:`\scriptstyle k_2 = 0.03` by default.

    The SSIM index satisfies the condition of symmetry:

    .. math::

        \text{SSIM}(x, y) = \text{SSIM}(y, x)

    Parameters
    ----------
    image: 2D ndarray
        The cleaned image returned by the image cleanning algorithm to assess.
    reference_image: 2D ndarray
        The actual clean image (the best result that can be expected for the
        image cleaning algorithm).

    Returns
    -------
    float
        The score of the image cleaning algorithm for the given image.

    References
    ----------
    .. [1] Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P.
       (2004). Image quality assessment: From error visibility to
       structural similarity. IEEE Transactions on Image Processing,
       13, 600-612.
       https://ece.uwaterloo.ca/~z70wang/publications/ssim.pdf,
       DOI:10.1.1.11.2477
    .. [2] Avanaki, A. N. (2009). Exact global histogram specification
       optimized for structural similarity. Optical Review, 16, 613-621.
       http://arxiv.org/abs/0901.0065,
       DOI:10.1007/s10043-009-0119-z
    .. [3] http://scikit-image.org/docs/dev/api/skimage.measure.html#compare-ssim
    .. [4] https://en.wikipedia.org/wiki/Structural_similarity
    """

    # Copy and cast images to prevent tricky bugs
    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
    image = image.astype('float64', copy=True)
    reference_image = reference_image.astype('float64', copy=True)

    # TODO: the following two lines may be wrong...
    image[np.isnan(image)] = 0
    reference_image[np.isnan(reference_image)] = 0

    ssim_val, ssim_image = ski_ssim(image, reference_image, full=True, gaussian_weights=True, sigma=0.5)

    return float(ssim_val)


# Peak Signal-to-Noise Ratio (PSNR) ###########################################

def psnr(image, reference_image):
    r"""Compute the score of ``image`` regarding ``reference_image``
    with the *Peak Signal-to-Noise Ratio* (PSNR) metric.

    See [5]_ and [6]_ for more information.
    
    Parameters
    ----------
    image: 2D ndarray
        The cleaned image returned by the image cleanning algorithm to assess.
    reference_image: 2D ndarray
        The actual clean image (the best result that can be expected for the
        image cleaning algorithm).

    Returns
    -------
    float
        The score of the image cleaning algorithm for the given image.

    References
    ----------
    .. [5] http://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.compare_psnr
    .. [6] https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio
    """

    # Copy and cast images to prevent tricky bugs
    # See https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.astype.html#numpy-ndarray-astype
    image = image.astype('float64', copy=True)
    reference_image = reference_image.astype('float64', copy=True)

    # TODO: the following two lines may be wrong...
    image[np.isnan(image)] = 0
    reference_image[np.isnan(reference_image)] = 0

    #psnr_val = ski_psnr(image, reference_image, dynamic_range=1e3)
    psnr_val = ski_psnr(image, reference_image, data_range=1e3)

    return float(psnr_val)


# Clusters of pixels ##########################################################

#def number_of_clusters(image, reference_image):
#    delta_pe, delta_abs_pe, delta_num_pixels = filter_pixels_clusters_stats(image)
#
#    score_dict = collections.OrderedDict((
#                    ('kill_isolated_pixels_delta_pe',         delta_pe),
#                    ('kill_isolated_pixels_delta_abs_pe',     delta_abs_pe),
#                    ('kill_isolated_pixels_delta_num_pixels', delta_num_pixels)
#                 ))
#
#    Score = collections.namedtuple('Score', score_dict.keys())
#
#    return Score(**score_dict)
