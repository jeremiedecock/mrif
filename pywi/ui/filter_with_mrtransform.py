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

from pywi.processing.compositing.filter_with_mrtransform import clean_image
from pywi.processing.filtering import hard_filter
from pywi.processing.transform import mrtransform_wrapper

from pywi.io.images import load_image, save_image
from pywi.io.plot import plot_list, mpl_save_list

from pywi.ui.argparse_commons import add_common_arguments


def add_arguments(parser):
    """Populate the given argparse.ArgumentParser with arguments.

    This function can be used to make the definition these argparse arguments
    reusable in other modules and avoid the duplication of these definitions
    among the executable scripts.

    The following arguments are added to the parser:

    - **type-of-filtering** (string): type of filtering
    - **filter-thresholds** (float list): thresholds used for the plane filtering.
    - **last-scale** (string): last plane treatment
    - **detect-only-positive-structures** (boolean): detect only positive structures.
    - **kill-isolated-pixels** (boolean): suppress isolated pixels in the support
      (scipy implementation)
    - **noise-cdf-file** (path): the JSON file containing the Cumulated
      Distribution Function of the noise model used to inject artificial noise
      in blank pixels (those with a NaN value)
    - **tmp-dir** (path): the directory where temporary files are written

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser to populate.

    Returns
    -------
    argparse.ArgumentParser
        Return the populated ArgumentParser object.
    """

    parser.add_argument("--type-of-filtering", "-f", metavar="STRING", default=hard_filter.DEFAULT_TYPE_OF_FILTERING,
                        help="Type of filtering: {}.".format(", ".join(hard_filter.AVAILABLE_TYPE_OF_FILTERING)))

    parser.add_argument("--filter-thresholds", "-t", metavar="FLOAT LIST", default=hard_filter.DEFAULT_FILTER_THRESHOLDS_STR,
                        help="Thresholds used for the plane filtering.")

    parser.add_argument("--last-scale", "-L", metavar="STRING", default=mrtransform_wrapper.DEFAULT_LAST_SCALE_TREATMENT,
                        help="Last plane treatment: {}.".format(", ".join(mrtransform_wrapper.AVAILABLE_LAST_SCALE_OPTIONS)))

    parser.add_argument("--detect-only-positive-structures", "-p", action="store_true",
                        help="Detect only positive structures.")

    parser.add_argument("--kill-isolated-pixels", action="store_true",
                        help="Suppress isolated pixels in the support (scipy implementation).")

    parser.add_argument("--noise-cdf-file", metavar="FILE",
                        help="The JSON file containing the Cumulated Distribution Function of the noise model used to inject artificial noise in blank pixels (those with a NaN value). Default=None.")

    parser.add_argument("--tmp-dir", default=".", metavar="DIRECTORY",
                        help="The directory where temporary files are written.")

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

    type_of_filtering = args.type_of_filtering
    filter_thresholds_str = args.filter_thresholds
    last_scale_treatment = args.last_scale
    detect_only_positive_structures = args.detect_only_positive_structures
    kill_isolated_pixels = args.kill_isolated_pixels
    noise_cdf_file = args.noise_cdf_file
    tmp_dir = args.tmp_dir

    verbose = args.verbose
    debug = args.debug
#    max_images = args.max_images
#    benchmark_method = args.benchmark
#    label = args.label
    plot = args.plot
    saveplot = args.saveplot

#    input_file_or_dir_path_list = args.fileargs
    input_file = args.fileargs[0]

    # CHECK OPTIONS #############################

    if type_of_filtering not in hard_filter.AVAILABLE_TYPE_OF_FILTERING:
        raise ValueError('Unknown type of filterning: "{}". Should be in {}'.format(type_of_filtering,
                                                                                    hard_filter.AVAILABLE_TYPE_OF_FILTERING))

    try:
        filter_thresholds = [float(threshold_str) for threshold_str in filter_thresholds_str.split(",")]
    except:
        raise ValueError('Wrong filter thresholds: "{}". Should be in a list of figures separated by a comma (e.g. "3,2,3")'.format(filter_thresholds_str))

    if last_scale_treatment not in mrtransform_wrapper.AVAILABLE_LAST_SCALE_OPTIONS:
        raise ValueError('Unknown type of last scale treatment: "{}". Should be in {}'.format(last_scale_treatment ,
                                                                                              mrtransform_wrapper.AVAILABLE_LAST_SCALE_OPTIONS))

    # TODO: check the noise_cdf_file value
    # TODO: check the tmp_dir value

    #############################################

    #if args.output is None:
    #    output_file_path = "score_wavelets_benchmark_{}.json".format(benchmark_method)
    #else:
    #    output_file_path = args.output

    ##if noise_cdf_file is not None:
    ##    noise_distribution = EmpiricalDistribution(noise_cdf_file)
    ##else:
    ##    noise_distribution = None
    noise_distribution = None

    # CLEAN THE INPUT IMAGE ###################################

    input_img = load_image(input_file)

    # Copy the image (otherwise some cleaning functions may change it)
    input_img_copy = input_img.astype('float64', copy=True)

    cleaned_img = clean_image(input_img_copy,
                              type_of_filtering=type_of_filtering,
                              filter_thresholds=filter_thresholds,
                              last_scale_treatment=last_scale_treatment,
                              detect_only_positive_structures=detect_only_positive_structures,
                              kill_isolated_pixels=kill_isolated_pixels,
                              noise_distribution=noise_distribution,
                              tmp_files_directory=tmp_dir)

    # PLOT IMAGES #########################################################

    if plot or (saveplot is not None):
        image_list = [input_img, cleaned_img] 
        title_list = ["Input image", "Filtered image"] 

        if plot:
            plot_list(image_list, title_list=title_list)

        if saveplot is not None:
            plot_file_path = saveplot
            print("Saving {}".format(plot_file_path))
            mpl_save_list(image_list,
                                 output_file_path=plot_file_path,
                                 title_list=title_list)

    # SAVE IMAGE ##########################################################

    basename, extension = os.path.splitext(input_file)
    output_file_path = "{}-out{}".format(basename, extension)
    save_image(cleaned_img, output_file_path)

if __name__ == "__main__":
    main()

