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

"""
Denoise FITS images with Wavelet Transform.

This script use mr_filter -- a program written CEA/CosmoStat
(www.cosmostat.org) -- to make Wavelet Transform.

Example usages:
  ./denoising_with_wavelets_mr_filter.py -h
  ./denoising_with_wavelets_mr_filter.py ./test.fits
  ipython3 -- ./denoising_with_wavelets_mr_filter.py -n4 ./test.fits

This script requires the mr_filter program
(http://www.cosmostat.org/software/isap/).
"""

__all__ = ['wavelet_transform']

import argparse
import os
import tempfile

import datapipe.denoising
from datapipe.denoising.abstract_cleaning_algorithm import AbstractCleaningAlgorithm
from datapipe.io import images


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

class WaveletTransform(AbstractCleaningAlgorithm):

    def __init__(self):
        super(WaveletTransform, self).__init__()
        self.label = "WT (mr_filter)"  # Name to show in plots

    def clean_image(self, input_img, number_of_scales=4):
        """
        Do the wavelet transform.

        mr_filter
        -K         Suppress the last scale (to have background pixels = 0)
        -k         Suppress isolated pixels in the support
        -F2        First scale used for the detection (smooth the resulting image)
        -C1        Coef_Detection_Method: K-SigmaNoise Threshold
        -s3        K-SigmaNoise Threshold = 3 sigma
        -m2        Noise model (try -m2 or -m10) -> -m10 works better but is much slower...

        eventuellement -w pour le debug
        -p  ?      Detect only positive structure
        -P  ?      Suppress the positivity constraint

        Raises
        ------
        WrongDimensionError
            If `cleaned_img` is not a 2D array.
        """

        if input_img.ndim != 2:
            raise WrongDimensionError()

        # Make a temporary directory to store fits files
        with tempfile.TemporaryDirectory() as temp_dir_path:

            input_file_path = os.path.join(temp_dir_path, "in.fits")
            mr_output_file_path = os.path.join(temp_dir_path, "out.fits")

            # WRITE THE INPUT FILE (FITS) ##########################

            try:
                images.save(input_img, input_file_path)
            except:
                print("Error on input FITS file:", input_file_path)
                raise

            # EXECUTE MR_FILTER ####################################

            # TODO: improve the following lines
            #cmd = 'mr_filter -K -k -C1 -s3 -m2 -p -P -n{} "{}" {}'.format(number_of_scales, input_file_path, mr_output_file_path)
            cmd = 'mr_filter -K -k -C1 -s3 -m3 -n{} "{}" {}'.format(number_of_scales, input_file_path, mr_output_file_path)

            try:
                os.system(cmd)
            except:
                print("Error on command:", cmd)
                raise

            # READ THE MR_FILTER OUTPUT FILE #######################

            try:
                cleaned_img = images.load(mr_output_file_path, 0)
            except:
                print("Error on output FITS file:", mr_output_file_path)
                raise

        # The temporary directory and all its contents are removed now

        if cleaned_img.ndim != 2:
            raise WrongDimensionError()

        return cleaned_img


def main():

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Denoise FITS images with Wavelet Transform.")

    parser.add_argument("--number_of_scales", "-n", type=int, default=4, metavar="INTEGER",
                        help="number of scales used in the multiresolution transform (default: 4)")

    # COMMON OPTIONS

    parser.add_argument("--benchmark", "-b", metavar="STRING", 
                        help="The benchmark method to use to assess the algorithm for the"
                             "given images")

    parser.add_argument("--plot", action="store_true",
                        help="Plot images")

    parser.add_argument("--saveplot", default=None, metavar="FILE",
                        help="The output file where to save plotted images")

    parser.add_argument("--output", "-o", default=None,
                        metavar="FILE",
                        help="The output file path (JSON)")

    parser.add_argument("fileargs", nargs="+", metavar="FILE",
                        help="The files image to process (FITS)."
                             "If fileargs is a directory,"
                             "all FITS files it contains are processed.")

    args = parser.parse_args()

    number_of_scales = args.number_of_scales
    benchmark_method = args.benchmark
    plot = args.plot
    saveplot = args.saveplot

    input_file_or_dir_path_list = args.fileargs

    if args.output is None:
        output_file_path = "score_wavelets_benchmark_{}.json".format(benchmark_method)
    else:
        output_file_path = args.output

    cleaning_function_params = {"number_of_scales": number_of_scales}

    cleaning_algorithm = WaveletTransform()
    cleaning_algorithm.run(cleaning_function_params,
                           input_file_or_dir_path_list,
                           benchmark_method,
                           output_file_path,
                           plot,
                           saveplot)


if __name__ == "__main__":
    main()

