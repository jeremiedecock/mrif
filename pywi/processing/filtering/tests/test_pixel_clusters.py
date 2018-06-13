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
This module contains unit tests for the "image.filter_pixels_clusters" module.
"""

from pywi.processing.filtering.pixel_clusters import filter_pixels_clusters, filter_pixels_clusters_stats

import numpy as np

import unittest


# Unit Tests based on the "unittest" package ##################################

class TestKillIsolatedPixels(unittest.TestCase):
    """
    Contains unit tests for the "denoising.filter_pixels_clusters" module.
    """

    # Test the "filter_pixels_clusters" function ##############################

    def test_whether_selection_is_based_on_pixels_value(self):
        """Check whether selection is based on pixels value or number of pixels in clusters."""

        # Input image #################

        input_img = np.array([[0, 0, 0, 0,  0, 0],
                              [1, 1, 1, 0,  0, 0],
                              [1, 1, 1, 0, 10, 0],
                              [1, 1, 1, 0,  0, 0],
                              [0, 0, 0, 0,  0, 0]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img)

        # Expected output image #######

        expected_output_img = np.array([[0, 0, 0, 0,  0, 0],
                                        [0, 0, 0, 0,  0, 0],
                                        [0, 0, 0, 0, 10, 0],
                                        [0, 0, 0, 0,  0, 0],
                                        [0, 0, 0, 0,  0, 0]])

        np.testing.assert_array_equal(output_img, expected_output_img)


    def test_kill_isolated_pixels_input_copy(self):
        """Check whether the input image is altered during process."""

        # Input image #################

        input_img = np.array([[1, 0, 1],
                              [1, 0, 0],
                              [1, 0, 1]])

        input_img_copy = np.copy(input_img)

        # Output image ################

        output_img = filter_pixels_clusters(input_img)

        # Check whether the input image has changed

        np.testing.assert_array_equal(input_img_copy, input_img)


    def test_kill_isolated_pixels_example1(self):
        """Check the output of the filter_pixels_clusters function."""

        # Input image #################

        input_img = np.array([[0, 0, 1, 1, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [1, 1, 0, 0, 1, 0],
                              [0, 0, 0, 1, 0, 0]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img)

        # Expected output image #######

        expected_output_img = np.array([[0, 0, 1, 1, 0, 0],
                                        [0, 0, 0, 1, 0, 0],
                                        [0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0]])

        np.testing.assert_array_equal(output_img, expected_output_img)


    def test_kill_isolated_pixels_example2(self):
        """Check the output of the filter_pixels_clusters function."""

        # Input image #################

        input_img = np.array([[0, 0, 1, 1, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [5, 1, 0, 0, 1, 0],
                              [0, 0, 0, 1, 0, 0]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img)

        # Expected output image #######

        expected_output_img = np.array([[0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0],
                                        [5, 1, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0]])

        np.testing.assert_array_equal(output_img, expected_output_img)


    def test_kill_isolated_pixels_example3(self):
        """Check the output of the filter_pixels_clusters function."""

        # Input image #################

        input_img = np.array([[0, 0,-1, 9, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [1, 1, 0, 0, 1, 0],
                              [0, 0, 0, 1, 0, 0]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img, threshold=0.2)

        # Expected output image #######

        expected_output_img = np.array([[0, 0, 0, 9, 0, 0],
                                        [0, 0, 0, 1, 0, 0],
                                        [0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0]])

        np.testing.assert_array_equal(output_img, expected_output_img)


    def test_kill_isolated_pixels_example_negative_threshold(self):
        """Check the output of the filter_pixels_clusters function."""

        # Input image #################

        input_img = np.array([[0, 0,  0,  0,  0, 0, 0],
                              [0, 0, -1, -1, -1, 0, 0],
                              [0, 0, -1, -1, -1, 0, 0],
                              [0, 0, -1, -1, -1, 0, 0],
                              [0, 0,  0,  0,  0, 0, 0]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img, threshold=-2)

        # Expected output image #######

        expected_output_img = np.array([[0, 0,  0,  0,  0, 0, 0],
                                        [0, 0, -1, -1, -1, 0, 0],
                                        [0, 0, -1, -1, -1, 0, 0],
                                        [0, 0, -1, -1, -1, 0, 0],
                                        [0, 0,  0,  0,  0, 0, 0]])  # < Here there is only one big island!

        np.testing.assert_array_equal(output_img, expected_output_img)


    def test_kill_isolated_pixels_example_threshold(self):
        """Check that every values below threshold is set to 0."""

        # Input image #################

        input_img = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                              [1.0, 0.1, 1.0, 1.0, 1.0, 0.1, 1.0],
                              [0.0, 0.5, 1.0,-1.0, 1.0, 0.5, 0.0],
                              [1.0, 0.1, 1.0, 1.0, 1.0, 0.1, 1.0],
                              [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img, threshold=0.2)

        # Expected output image #######

        expected_output_img = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.5, 1.0, 0.0, 1.0, 0.5, 0.0],
                                        [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])

        np.testing.assert_array_equal(output_img, expected_output_img)


    def test_kill_isolated_pixels_example_nan_1(self):
        """Check the output of the filter_pixels_clusters function."""

        # Input image #################

        input_img = np.array([[np.nan, 0, 1, 1, 0, np.nan],
                              [     0, 0, 0, 1, 0,      0],
                              [     5, 1, 0, 0, 1,      0],
                              [np.nan, 0, 0, 1, 0, np.nan]])

        # Output image ################

        output_img = filter_pixels_clusters(input_img)

        # Expected output image #######

        expected_output_img = np.array([[np.nan, 0, 0, 0, 0, np.nan],
                                        [     0, 0, 0, 0, 0,      0],
                                        [     5, 1, 0, 0, 0,      0],
                                        [np.nan, 0, 0, 0, 0, np.nan]])

        np.testing.assert_array_equal(output_img, expected_output_img)


    # Test the "filter_pixels_clusters_stats" function ##########################

    def test_kill_isolated_pixels_stats_example1(self):
        """Check the output of the filter_pixels_clusters_stats function."""

        # Input image #################

        input_img = np.array([[0, 0, 1, 9, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [1, 3, 0, 0, 5, 0],
                              [0, 0, 0, 1, 0, 0]])

        # Output image ################

        delta_pe, delta_abs_pe, delta_num_pixels = filter_pixels_clusters_stats(input_img)

        # Expected output image #######

        expected_delta_pe = 10
        expected_delta_abs_pe = 10
        expected_delta_num_pixels = 4

        self.assertEqual(delta_pe, expected_delta_pe)
        self.assertEqual(delta_abs_pe, expected_delta_abs_pe)
        self.assertEqual(delta_num_pixels, expected_delta_num_pixels)


    def test_kill_isolated_pixels_stats_example2(self):
        """Check the output of the filter_pixels_clusters_stats function."""

        # Input image #################

        input_img = np.array([[0, 0, 1, 9, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [1,-3, 0, 0,-5, 0],
                              [0, 0, 0, 1, 0, 0]])

        # Output image ################

        delta_pe, delta_abs_pe, delta_num_pixels = filter_pixels_clusters_stats(input_img)

        # Expected output image #######

        expected_delta_pe = -6
        expected_delta_abs_pe = 10
        expected_delta_num_pixels = 4

        self.assertEqual(delta_pe, expected_delta_pe)
        self.assertEqual(delta_abs_pe, expected_delta_abs_pe)
        self.assertEqual(delta_num_pixels, expected_delta_num_pixels)


    def test_kill_isolated_pixels_stats_example3(self):
        """Check the output of the filter_pixels_clusters_stats function."""

        # Input image #################

        input_img = np.array([[0, 0,-1, 9, 0, 0],
                              [0, 0, 0, 1, 0, 0],
                              [1, 3, 0, 0, 5, 0],
                              [0, 0, 0, 1, 0, 0]])

        # Output image ################

        delta_pe, delta_abs_pe, delta_num_pixels = filter_pixels_clusters_stats(input_img, threshold=None)

        # Expected output image #######

        expected_delta_pe = 9
        expected_delta_abs_pe = 11
        expected_delta_num_pixels = 5

        self.assertEqual(delta_pe, expected_delta_pe)
        self.assertEqual(delta_abs_pe, expected_delta_abs_pe)
        self.assertEqual(delta_num_pixels, expected_delta_num_pixels)


    def test_kill_isolated_pixels_stats_example_nan_1(self):
        """Check the output of the filter_pixels_clusters_stats function."""

        # Input image #################

        input_img = np.array([[np.nan, 0, 1, 3, 0, np.nan],
                              [     0, 0, 0, 1, 0,      0],
                              [     5, 1, 0, 0, 1,      0],
                              [np.nan, 0, 0, 1, 0, np.nan]])

        # Output image ################

        delta_pe, delta_abs_pe, delta_num_pixels = filter_pixels_clusters_stats(input_img, threshold=None)

        # Expected output image #######

        expected_delta_pe = 7
        expected_delta_abs_pe = 7
        expected_delta_num_pixels = 5

        self.assertEqual(delta_pe, expected_delta_pe)
        self.assertEqual(delta_abs_pe, expected_delta_abs_pe)
        self.assertEqual(delta_num_pixels, expected_delta_num_pixels)
    

if __name__ == '__main__':
    unittest.main()

