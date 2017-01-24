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

import copy
import datetime
import json
import os
import math
import numpy as np
import sys
import time
import traceback

from datapipe.image.hillas_parameters import get_hillas_parameters

from datapipe.image.kill_isolated_pixels import kill_isolated_pixels
from datapipe.image.kill_isolated_pixels import kill_isolated_pixels_stats

from datapipe.image.signal_to_border_distance import signal_to_border
from datapipe.image.signal_to_border_distance import signal_to_border_distance

from datapipe.benchmark import assess
from datapipe.io import images

# TODO:
# - maj les modules de Tino

###############################################################################

class AbstractCleaningAlgorithm(object):

    def __init__(self):
        self.label = "Unknown"  # Name to show in plots
        self.verbose = False    # Debug mode

    def __call__(self, *pargs, **kargs):
        return self.clean_image(*pargs, **kargs)

    # STR #####################################################################

    def __str__(self):
        return "{}".format(self.algorithm_label)

    def run(self,
            cleaning_function_params,
            input_file_or_dir_path_list,
            benchmark_method,
            output_file_path,
            plot=False,
            saveplot=None):

        image_counter = 0

        if benchmark_method is not None:
            io_list = []

        for input_file_or_dir_path in input_file_or_dir_path_list:

            if os.path.isdir(input_file_or_dir_path):
                input_file_path_list = []
                for dir_item in os.listdir(input_file_or_dir_path):
                    dir_item_path = os.path.join(input_file_or_dir_path, dir_item)
                    if dir_item_path.lower().endswith('.fits') and os.path.isfile(dir_item_path):
                        input_file_path_list.append(dir_item_path)
            else:
                input_file_path_list = [input_file_or_dir_path]

            for input_file_path in input_file_path_list:

                image_counter += 1
                print("* {}: PROCESS IMAGE NUMBER {}".format(self.label, image_counter))

                # CLEAN ONE IMAGE #########################################################

                image_dict = {"input_file_path": input_file_path}

                try:
                    # READ THE INPUT FILE #################################################

                    fits_images_dict, fits_metadata_dict = images.load_benchmark_images(input_file_path)

                    input_img = fits_images_dict["input_image"]
                    reference_img = fits_images_dict["reference_image"]

                    image_dict.update(fits_metadata_dict)

                    # CLEAN THE INPUT IMAGE ###############################################

                    # Copy the image (otherwise some cleaning functions like Tailcut may change it)
                    #input_img_copy = copy.deepcopy(input_img)
                    input_img_copy = input_img.astype('float64', copy=True)

                    initial_time = time.perf_counter()
                    cleaned_img = self.clean_image(input_img_copy, **cleaning_function_params)
                    execution_time = time.perf_counter() - initial_time

                    # ASSESS OR PRINT THE CLEANED IMAGE ###################################

                    if benchmark_method is not None:
                        score_tuple, score_name_tuple = assess.assess_image_cleaning(input_img,
                                                                                     cleaned_img,
                                                                                     reference_img,
                                                                                     benchmark_method)

                        # IMAGE METADATA
                        image_dict["score"] = score_tuple
                        image_dict["score_name"] = score_name_tuple
                        image_dict["execution_time"] = execution_time
                        image_dict["img_ref_signal_to_border"] = signal_to_border(reference_img)
                        image_dict["img_ref_signal_to_border_distance"] = signal_to_border_distance(reference_img)

                        delta_pe, delta_abs_pe, delta_num_pixels = kill_isolated_pixels_stats(reference_img)

                        image_dict["img_ref_delta_pe"] = delta_pe
                        image_dict["img_ref_delta_abs_pe"] = delta_abs_pe
                        image_dict["img_ref_delta_num_pixels"] = delta_num_pixels

                        #hillas_params_1 = get_hillas_parameters(reference_img, 1)

                        #image_dict["img_ref_hillas_1_size"] =   hillas_params_1.size
                        #image_dict["img_ref_hillas_1_cen_x"] =  hillas_params_1.cen_x.value
                        #image_dict["img_ref_hillas_1_cen_y"] =  hillas_params_1.cen_y.value
                        #image_dict["img_ref_hillas_1_length"] = hillas_params_1.length.value
                        #image_dict["img_ref_hillas_1_width"] =  hillas_params_1.width.value
                        #image_dict["img_ref_hillas_1_r"] =      hillas_params_1.r
                        #image_dict["img_ref_hillas_1_phi"] =    hillas_params_1.phi
                        #image_dict["img_ref_hillas_1_psi"] =    hillas_params_1.psi.value
                        #image_dict["img_ref_hillas_1_miss"] =   hillas_params_1.miss.value

                        hillas_params_2 = get_hillas_parameters(reference_img, 2)

                        image_dict["img_ref_hillas_2_size"] =   hillas_params_2.size
                        image_dict["img_ref_hillas_2_cen_x"] =  hillas_params_2.cen_x.value
                        image_dict["img_ref_hillas_2_cen_y"] =  hillas_params_2.cen_y.value
                        image_dict["img_ref_hillas_2_length"] = hillas_params_2.length.value
                        image_dict["img_ref_hillas_2_width"] =  hillas_params_2.width.value
                        image_dict["img_ref_hillas_2_r"] =      hillas_params_2.r
                        image_dict["img_ref_hillas_2_phi"] =    hillas_params_2.phi
                        image_dict["img_ref_hillas_2_psi"] =    hillas_params_2.psi.value
                        image_dict["img_ref_hillas_2_miss"] =   hillas_params_2.miss.value

                    # PLOT IMAGES #########################################################

                    if plot or (saveplot is not None):
                        image_list = [input_img, reference_img, cleaned_img] 
                        title_list = ["Input image", "Reference image", "Cleaned image"] 

                        if plot:
                            images.plot_list(image_list, title_list, fits_metadata_dict)

                        if saveplot is not None:
                            if len(input_file_or_dir_path_list) > 1:
                                basename, extension = os.path.splitext(saveplot)
                                plot_file_path = "{}_E{}_T{}{}".format(basename, fits_metadata_dict["event_id"], fits_metadata_dict["tel_id"], extension)
                            else:
                                plot_file_path = saveplot

                            print("Saving {}".format(plot_file_path))
                            images.mpl_save_list(image_list, plot_file_path, title_list, fits_metadata_dict)

                except Exception as e:
                    print("Abort image {}: {} ({})".format(input_file_path, e, type(e)))
                    #traceback.print_tb(e.__traceback__, file=sys.stdout)

                    if benchmark_method is not None:
                        error_dict = {"type": str(type(e)),
                                      "message": str(e)}
                        image_dict["error"] = error_dict

                finally:
                    if benchmark_method is not None:
                        io_list.append(image_dict)

        if benchmark_method is not None:
            error_list = [image_dict["error"] for image_dict in io_list if "error" in image_dict]
            print("{} images aborted".format(len(error_list)))

            # GENERAL EXPERIMENT METADATA
            output_dict = {}
            output_dict["date_time"] = str(datetime.datetime.now())
            output_dict["class_name"] = self.__class__.__name__
            output_dict["algo_code_ref"] = str(self.__class__.clean_image.__code__)
            output_dict["label"] = self.label
            output_dict["algo_params"] = cleaning_function_params
            output_dict["benchmark_method"] = benchmark_method
            output_dict["system"] = " ".join(os.uname())
            output_dict["io"] = io_list

            with open(output_file_path, "w") as fd:
                json.dump(output_dict, fd, sort_keys=True, indent=4)  # pretty print format
