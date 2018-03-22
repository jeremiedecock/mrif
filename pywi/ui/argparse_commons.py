#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Jérémie DECOCK (http://www.jdhp.org)

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

def add_common_arguments(parser, nargs=1):
    """Populate the given argparse.ArgumentParser with arguments.

    This function can be used to centralize the definition of commons argparse
    arguments and avoid the duplication of these definitions among the
    executable scripts.

    The following arguments are added to the parser:

    - **verbose** (boolean): verbose mode
    - **debug** (boolean): debug mode
    - **plot** (boolean): plot images
    - **saveplot** (string): the output file where to save plotted images
    - **fileargs** (file paths): the files image to process

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser to populate.

    Returns
    -------
    argparse.ArgumentParser
        Return the populated ArgumentParser object.
    """

    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose mode.")

    parser.add_argument("--debug", action="store_true",
                        help="Debug mode.")

#    parser.add_argument("--max-images", type=int, metavar="INTEGER",
#                        help="The maximum number of images to process")

#    parser.add_argument("--benchmark", "-b", metavar="STRING",
#                        help="The benchmark method to use to assess the algorithm for the"
#                             "given images")

#    parser.add_argument("--label", "-l", default=None,
#                        metavar="STRING",
#                        help="The label attached to the produced results")

    parser.add_argument("--plot", action="store_true",
                        help="Plot images.")

    parser.add_argument("--saveplot", default=None, metavar="FILE",
                        help="The output file where to save plotted images.")

#    parser.add_argument("--output", "-o", default=None,
#                        metavar="FILE",
#                        help="The output file path (JSON)")

#    parser.add_argument("fileargs", nargs="+", metavar="FILE",
    parser.add_argument("fileargs", nargs=nargs, metavar="FILE",
                        help="The files image to process.")
#                             "If fileargs is a directory,"
#                             "all FITS files it contains are processed.")

    return parser
