# -*- coding: utf-8 -*-

# Copyright (c) 2015 Jérémie DECOCK (http://www.jdhp.org)

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

from gi.repository import Gtk as gtk

import json
import math
import os

from mrif.io import images

class ImagesListModel(object):

    def __init__(self, input_directory_path):

        self.input_directory_path = input_directory_path

        # Parse the input directory
        self.fits_file_name_list = get_fits_files_list(input_directory_path)

        # Parse FITS files
        self.fits_metadata_list = parse_fits_files(self.input_directory_path, self.fits_file_name_list)

        # Creating the gtk.ListStore model
        self.liststore = gtk.ListStore(int,    # Event ID
                                       int,    # Tel ID
                                       float,  # MC energy
                                       float,  # NPE
                                       str)    # File name

        for image_metadata_dict in self.fits_metadata_list:
            event_id = image_metadata_dict["event_id"]
            tel_id = image_metadata_dict["tel_id"]
            mc_energy = image_metadata_dict["mc_energy"]
            npe = image_metadata_dict["npe"]
            file_name = image_metadata_dict["file_name"]

            self.liststore.append([event_id, tel_id, mc_energy, npe, file_name])


def get_fits_files_list(directory_path):

    # Parse the input directory
    print("Parsing", directory_path)

    fits_file_name_list = [file_name
                       for file_name
                       in os.listdir(directory_path)
                       if os.path.isfile(os.path.join(directory_path, file_name))
                       and file_name.endswith((".fits", ".fit"))]

    return fits_file_name_list


def parse_fits_files(dir_name, fits_file_name_list):
    fits_metadata_list = []

    # Parse the input files
    mc_energy_unit = None

    for file_index, file_name in enumerate(fits_file_name_list):
        metadata_dict = {}

        # Read the input file #########

        fits_images_dict, fits_metadata_dict = images.load_benchmark_images(os.path.join(dir_name, file_name))

        # Fill the dict ###############
        
        if mc_energy_unit is None:
            mc_energy_unit = fits_metadata_dict["mc_energy_unit"] # TODO
        else:
            if mc_energy_unit != fits_metadata_dict["mc_energy_unit"]:
                raise Exception("Inconsistent data")

        metadata_dict["event_id"] = fits_metadata_dict["event_id"]
        metadata_dict["tel_id"] = fits_metadata_dict["tel_id"]
        metadata_dict["mc_energy"] = fits_metadata_dict["mc_energy"]
        metadata_dict["npe"] = fits_metadata_dict["npe"]
        metadata_dict["file_name"] = file_name

        fits_metadata_list.append(metadata_dict)

        # Progress bar ################
        num_files = len(fits_file_name_list)
        relative_steps = math.ceil(num_files / 100.)

        if (file_index % relative_steps) == 0:
            progress_str = "{:.2f}% ({}/{})".format((file_index + 1)/num_files * 100,
                                                file_index + 1,
                                                num_files)
            print(progress_str)

    return fits_metadata_list 

