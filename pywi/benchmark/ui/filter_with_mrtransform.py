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

__all__ = ['add_arguments']

"""Denoise images with Wavelet Transform.

This script use mr_transform -- a program written CEA/CosmoStat
(www.cosmostat.org) -- to make Wavelet Transform.

Usage
-----

    filter_with_mrtransform.py [-h] [--type-of-filtering STRING]
                                    [--filter-thresholds FLOAT LIST]
                                    [--last-scale STRING]
                                    [--detect-only-positive-structures]
                                    [--kill-isolated-pixels]
                                    [--noise-cdf-file FILE] [--tmp-dir DIRECTORY]
                                    [--verbose] [--debug] [--max-images INTEGER]
                                    [--telid INTEGER] [--eventid INTEGER]
                                    [--camid STRING] [--benchmark STRING]
                                    [--label STRING] [--plot] [--saveplot FILE]
                                    [--output FILE]
                                    FILE [FILE ...]

    Denoise images with Wavelet Transform.

    positional arguments:
      FILE                  The files image to process. If fileargs is a
                            directory, all files it contains are processed.

    optional arguments:
      -h, --help            show this help message and exit
      --type-of-filtering STRING, -f STRING
                            Type of filtering: hard_filtering,
                            ksigma_hard_filtering
      --filter-thresholds FLOAT LIST, -t FLOAT LIST
                            Thresholds used for the plane filtering.
      --last-scale STRING, -L STRING
                            Last plane treatment: keep, drop, mask
      --detect-only-positive-structures, -p
                            Detect only positive structure
      --kill-isolated-pixels
                            Suppress isolated pixels in the support (scipy
                            implementation)
      --noise-cdf-file FILE
                            The JSON file containing the Cumulated Distribution
                            Function of the noise model used to inject artificial
                            noise in blank pixels (those with a NaN value).
                            Default=None.
      --tmp-dir DIRECTORY   The directory where temporary files are written.
      --verbose, -v         Verbose mode
      --debug               Debug mode
      --plot                Plot images
      --saveplot FILE       The output file where to save plotted images
      --output FILE, -o FILE
                            The output file path (JSON)

Examples
--------
  ./filter_with_mrtransform.py -h
  ./filter_with_mrtransform.py ./test.fits
  ipython3 -- ./filter_with_mrtransform.py -t 21.5,11.7 ./test.fits

Notes
-----
This script requires the mr_transform program
(http://www.cosmostat.org/software/isap/).

It also requires Numpy and Matplotlib Python libraries.
"""

import argparse
import os

from pywi.benchmark.core import benchmark
from pywi.benchmark.io.refbased import fits
from pywi.benchmark.metrics.refbased import mse
from pywi.benchmark.ui.argparse_commons import add_common_arguments

from pywi.processing.compositing.filter_with_mrtransform import clean_image


def add_arguments(parser):
    """Populate the given argparse.ArgumentParser with arguments.

    This function can be used to make the definition these argparse arguments
    reusable in other modules and avoid the duplication of these definitions
    among the executable scripts.

    The following arguments are added to the parser:

    - **...** (...): ...

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser to populate.

    Returns
    -------
    argparse.ArgumentParser
        Return the populated ArgumentParser object.
    """

    return parser


def main():
    """The main module execution function.

    Contains the instructions executed when the module is not imported but
    directly called from the system command line.
    """

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Filter images with Wavelet Transform.")

    parser = add_arguments(parser)
    parser = add_common_arguments(parser)

    args = parser.parse_args()

#    type_of_filtering = args.type_of_filtering
#    filter_thresholds_str = args.filter_thresholds
#    last_scale_treatment = args.last_scale
#    detect_only_positive_structures = args.detect_only_positive_structures
#    filter_pixels_clusters = args.filter_pixels_clusters
#    noise_cdf_file = args.noise_cdf_file
#    tmp_dir = args.tmp_dir
#
#    verbose = args.verbose
#    debug = args.debug
##    max_images = args.max_images
##    benchmark_method = args.benchmark
##    label = args.label
#    plot = args.plot
#    saveplot = args.saveplot
#
##    input_file_or_dir_path_list = args.fileargs
#    input_file = args.fileargs[0]
#
#    # CHECK OPTIONS #############################
#
#    if type_of_filtering not in hard_filter.AVAILABLE_TYPE_OF_FILTERING:
#        raise ValueError('Unknown type of filterning: "{}". Should be in {}'.format(type_of_filtering,
#                                                                                    hard_filter.AVAILABLE_TYPE_OF_FILTERING))
#
#    try:
#        filter_thresholds = [float(threshold_str) for threshold_str in filter_thresholds_str.split(",")]
#    except:
#        raise ValueError('Wrong filter thresholds: "{}". Should be in a list of figures separated by a comma (e.g. "3,2,3")'.format(filter_thresholds_str))
#
#    if last_scale_treatment not in mrtransform_wrapper.AVAILABLE_LAST_SCALE_OPTIONS:
#        raise ValueError('Unknown type of last scale treatment: "{}". Should be in {}'.format(last_scale_treatment ,
#                                                                                              mrtransform_wrapper.AVAILABLE_LAST_SCALE_OPTIONS))
#
#    cleaned_img = img_filter.clean_image(input_img_copy,
#                                         type_of_filtering=type_of_filtering,
#                                         filter_thresholds=filter_thresholds,
#                                         last_scale_treatment=last_scale_treatment,
#                                         detect_only_positive_structures=detect_only_positive_structures,
#                                         filter_pixels_clusters=filter_pixels_clusters,
#                                         noise_distribution=noise_distribution,
#                                         tmp_files_directory=tmp_dir)

    #############################################

#    gen = fits.benchmark_image_generator(["dirname"])
#    processing = clean_image
#
#    benchmark(benchmark_image_generator=gen,
#              processing=processing,
#              metrics=mse)


if __name__ == "__main__":
    main()

