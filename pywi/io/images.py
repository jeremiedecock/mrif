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
           'image_generator',
           'load_image',
           'load_fits',
           'mpl_save',
           'plot',
           'save_fits',
           'save_image']

import math

import collections

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Ellipse

import PIL.Image as pil_image     # PIL.Image is a module not a class...

import os

from astropy.io import fits

import pandas as pd

DEBUG = False

# EXCEPTIONS #################################################################

class FitsError(Exception):
    pass

class WrongHDUError(FitsError):
    """Exception raised when trying to access a wrong HDU in a FITS file.

    Attributes:
        file_path -- the FITS file concerned by the error
        hdu_index -- the HDU index concerned by the error
    """

    def __init__(self, file_path, hdu_index):
        super().__init__("File {} doesn't have data in HDU {}.".format(file_path, hdu_index))
        self.file_path = file_path
        self.hdu_index = hdu_index

class NotAnImageError(FitsError):
    """Exception raised when trying to load a FITS file which doesn't contain a
    valid image in the given HDU.

    Attributes:
        file_path -- the FITS file concerned by the error
        hdu_index -- the HDU index concerned by the error
    """

    def __init__(self, file_path, hdu_index):
        super().__init__("HDU {} in file {} doesn't contain any image.".format(hdu_index, file_path))
        self.file_path = file_path
        self.hdu_index = hdu_index

class WrongDimensionError(FitsError):
    """ Exception raised when trying to save a FITS with more than 3 dimensions
    or less than 2 dimensions.
    """

    def __init__(self):
        super().__init__("The input image should be a 2D or a 3D numpy array.")

class WrongFitsFileStructure(FitsError):
    """Exception raised when trying to load a FITS file which doesn't contain a
    valid structure (for benchmark).

    Attributes:
        file_path -- the FITS file concerned by the error
    """

    def __init__(self, file_path):
        super().__init__("File {} doesn't contain a valid structure.".format(file_path))
        self.file_path = file_path


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


# LOAD IMAGES ################################################################

def image_generator(path_list,
                    max_num_images=None,
                    **kwargs):
    """Return an iterable sequence all calibrated images in `path_list`.

    Parameters
    ----------
    path_list
        The path of files containing the images to extract. It can contain
        FITS/Simtel files and directories.
    max_num_images
        The maximum number of images to iterate.

    Yields
    ------
    Image1D or Image2D
        The named tuple `Image1D` or `Image1D` of the next FITS or Simtel files
        in `path_list`.
    """

    images_counter = 0

    for file_path in image_files_in_paths(path_list):
        if (max_num_images is not None) and (images_counter >= max_num_images):
            break
        else:
            if file_path.lower().endswith((".fits", ".fit")):
                # FITS FILES
                image_dict, fits_metadata_dict = load_benchmark_images(file_path)   # TODO: named tuple
                images_counter += 1
                yield Image2D(**image_dict, meta=fits_metadata_dict)
            else:
                raise Exception("Wrong item:", file_path)


# LOAD AND SAVE FITS FILES ###################################################

def load_benchmark_images(input_file_path):
    """Return images contained in the given FITS file.

    Parameters
    ----------
    input_file_path : str
        The path of the FITS file to load

    Returns
    -------
    dict
        A dictionary containing the loaded images and their metadata

    Raises
    ------
    WrongFitsFileStructure
        If `input_file_path` doesn't contain a valid structure
    """

    hdu_list = fits.open(input_file_path)   # open the FITS file

    # METADATA ################################################################

    hdu0 = hdu_list[0]

    metadata_dict = {}

    metadata_dict['version'] = hdu0.header['version']
    #metadata_dict['cam_id'] = hdu0.header['cam_id']

    # IMAGES ##################################################################

    if metadata_dict['version'] == 1:
        if (len(hdu_list) != 2) or (not hdu_list[0].is_image) or (not hdu_list[1].is_image):
            hdu_list.close()
            raise WrongFitsFileStructure(input_file_path)

        hdu0, hdu1 = hdu_list

        # IMAGES

        images_dict = {}

        images_dict["input_image"] = hdu0.data        # "hdu.data" is a Numpy Array
        images_dict["reference_image"] = hdu1.data    # "hdu.data" is a Numpy Array
    else:
        raise Exception("Unknown version number")

    # METADATA ################################################################

    metadata_dict['npe'] = float(np.nansum(images_dict["reference_image"]))       # np.sum() returns numpy.int64 objects thus it must be casted with float() to avoid serialization errors with JSON...
    metadata_dict['min_npe'] = float(np.nanmin(images_dict["reference_image"]))   # np.min() returns numpy.int64 objects thus it must be casted with float() to avoid serialization errors with JSON...
    metadata_dict['max_npe'] = float(np.nanmax(images_dict["reference_image"]))   # np.max() returns numpy.int64 objects thus it must be casted with float() to avoid serialization errors with JSON...

    hdu_list.close()

    return images_dict, metadata_dict   # TODO: named tuple


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
        image_array = load_fits(input_file_path, **kwargs)
    else:
        pil_img = pil_image.open(input_file_path)
        pil_img = pil_img.convert('L')
        image_array = np.array(pil_img)  # It works also with .png, .jpg, tiff, ...

    return image_array


def load_fits(input_file_path, hdu_index=0):
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
        save_fits(image_array, output_file_path, **kwargs)
    else:
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


def save_fits(img, output_file_path):
    """Save the `img` image (array_like) to the `output_file_path` FITS file.

    Parameters
    ----------
    img : array_like
        The image to save (should be a 2D or a 3D numpy array)
    output_file_path : str
        The path of the FITS file where to save the `img`

    Raises
    ------
    WrongDimensionError
        If `img` has more than 3 dimensions or less than 2 dimensions.
    """

    if img.ndim not in (2, 3):
        raise WrongDimensionError()

    hdu = fits.PrimaryHDU(img)

    hdu.writeto(output_file_path, overwrite=True)  # overwrite=True: overwrite the file if it already exists


# MATPLOTLIB ##################################################################

COLOR_MAP = cm.gnuplot2

def mpl_save(img, output_file_path, title=""):
    """
    img should be a 2D numpy array.
    """
    fig = plt.figure(figsize=(8.0, 8.0))
    ax = fig.add_subplot(111)
    ax.set_title(title, fontsize=24)

    #im = ax.imshow(img,
    #               origin='lower',
    #               interpolation='nearest',
    #               vmin=min(img.min(), 0),
    #               cmap=COLOR_MAP)

    # Manage NaN values (see http://stackoverflow.com/questions/2578752/how-can-i-plot-nan-values-as-a-special-color-with-imshow-in-matplotlib and http://stackoverflow.com/questions/38800532/plot-color-nan-values)
    masked = np.ma.masked_where(np.isnan(img), img)

    cmap = COLOR_MAP
    cmap.set_bad('black')
    im = ax.imshow(masked,
                   origin='lower',
                   interpolation='nearest',
                   cmap=cmap)

    plt.colorbar(im) # draw the colorbar

    plt.savefig(output_file_path, bbox_inches='tight')
    plt.close('all')


def plot(img, title=""):
    """
    img should be a 2D numpy array.
    """
    fig = plt.figure(figsize=(8.0, 8.0))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    #im = ax.imshow(img,
    #               origin='lower',
    #               interpolation='nearest',
    #               vmin=min(img.min(), 0),
    #               cmap=COLOR_MAP)

    # Manage NaN values (see http://stackoverflow.com/questions/2578752/how-can-i-plot-nan-values-as-a-special-color-with-imshow-in-matplotlib and http://stackoverflow.com/questions/38800532/plot-color-nan-values)
    masked = np.ma.masked_where(np.isnan(img), img)

    cmap = COLOR_MAP
    cmap.set_bad('black')
    im = ax.imshow(masked,
                   origin='lower',
                   interpolation='nearest',
                   cmap=cmap)

    plt.colorbar(im) # draw the colorbar

    plt.show()


def plot_hist(img, num_bins=50, logx=False, logy=False, x_max=None, title=""):
    """
    """

    # Flatten + remove NaN values
    flat_img = img[np.isfinite(img)]

    fig = plt.figure(figsize=(8.0, 8.0))
    ax = fig.add_subplot(111)
    ax.set_title(title)

    if logx:
        # Setup the logarithmic scale on the X axis
        vmin = np.log10(flat_img.min())
        vmax = np.log10(flat_img.max())
        bins = np.logspace(vmin, vmax, num_bins) # Make a range from 10**vmin to 10**vmax
    else:
        bins = num_bins

    if x_max is not None:
        ax.set_xlim(xmax=x_max)

    res_tuple = ax.hist(flat_img,
                        bins=bins,
                        log=logy,               # Set log scale on the Y axis
                        histtype='bar',
                        alpha=1)

    if logx:
        ax.set_xscale("log")               # Activate log scale on X axis

    plt.show()



def _plot_list(img_list,
               title_list=None,
               highlight_mask_list=None,
               main_title=None):
    """Plot several images at once."""
    num_imgs = len(img_list)

    fig, ax_tuple = plt.subplots(nrows=1, ncols=num_imgs, figsize=(num_imgs*6, 6))

    if title_list is None:
        title_list = [None for i in img_list]

    if highlight_mask_list is None:
        highlight_mask_list = [None for i in img_list]

    for ax, img, title in zip(ax_tuple, img_list, title_list):
        masked = np.ma.masked_where(np.isnan(img), img)

        cmap = COLOR_MAP
        cmap.set_bad('black')
        im = ax.imshow(masked,
                       origin='lower',
                       interpolation='nearest',
                       cmap=cmap)

        ax.set_title(title)
        plt.colorbar(im, ax=ax) # draw the colorbar

    if main_title is not None:
        fig.suptitle(main_title, fontsize=18)
        plt.subplots_adjust(top=0.85)


def plot_list(img_list,
              title_list=None,
              highlight_mask_list=None,
              metadata_dict=None):
    """Plot several images at once.

    Parameters
    ----------
    img_list
        A list of 2D numpy array to plot.
    """

    # Main title
    main_title = None

    _plot_list(img_list,
               title_list=title_list,
               highlight_mask_list=highlight_mask_list,
               main_title=main_title)

    plt.show()


def mpl_save_list(img_list,
                  output_file_path,
                  title_list=None,
                  highlight_mask_list=None,
                  metadata_dict=None):
    """Plot several images at once.

    Parameters
    ----------
    img_list
        A list of 2D numpy array to plot.
    """

    # Main title
    main_title = None

    _plot_list(img_list,
               title_list=title_list,
               highlight_mask_list=highlight_mask_list,
               main_title=main_title)

    plt.savefig(output_file_path, bbox_inches='tight')
    plt.close('all')


# DEBUG #######################################################################

def export_image_as_plain_text(image, output_file_path):
    fd = open(output_file_path, 'w')
    for x in image:
        for y in x:
            print("{:5.2f}".format(y), end=" ", file=fd)
        print("", file=fd)
    fd.close()
