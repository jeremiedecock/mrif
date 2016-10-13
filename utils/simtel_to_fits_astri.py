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
... TODO
"""

__all__ = ['extract_images',
           'save_fits']

import argparse
from astropy.io import fits
import numpy as np
import os

import ctapipe
from ctapipe.io.hessio import hessio_event_source
import pyhessio

import datapipe.io.montecarlo_calibration_astri as mc_calibration
import datapipe.io.geometry_converter as geom_converter


DEFAULT_TEL_FILTER = list(range(1, 34))   # TODO


def extract_images(simtel_file_path,
                   tel_id_filter_list=None,
                   event_id_filter_list=None,
                   output_directory=None):

    # EXTRACT IMAGES ##########################################################

    # hessio_event_source returns a Python generator that streams data from an
    # EventIO/HESSIO MC data file (e.g. a standard CTA data file).
    # This generator contains ctapipe.core.Container instances ("event").
    # 
    # Parameters:
    # - max_events: maximum number of events to read
    # - allowed_tels: select only a subset of telescope, if None, all are read.
    source = hessio_event_source(simtel_file_path, allowed_tels=tel_id_filter_list)

    # ITERATE OVER EVENTS #####################################################

    for event in source:

        event_id = int(event.dl0.event_id)

        if (event_id_filter_list is None) or (event_id in event_id_filter_list):

            print("event", event_id)

            # ITERATE OVER IMAGES #############################################

            for tel_id in event.trig.tels_with_trigger:

                tel_id = int(tel_id)

                if tel_id in tel_id_filter_list:

                    print("telescope", tel_id)

                    # CHECK THE IMAGE GEOMETRY (ASTRI ONLY) ###################

                    # TODO

                    print("checking geometry")

                    x, y = event.meta.pixel_pos[tel_id]
                    foclen = event.meta.optical_foclen[tel_id]
                    geom = ctapipe.io.CameraGeometry.guess(x, y, foclen)

                    if (geom.pix_type != "rectangular") or (geom.cam_id != "ASTRI"):
                        raise ValueError("Telescope {}: error (the input image is not a valide ASTRI telescope image)".format(tel_id))

                    # GET AND CROP THE IMAGE ##################################

                    # uncalibrated_image = [1D numpy array of channel1, 1D numpy array of channel2]
                    # calibrated_image = 1D numpy array

                    print("calibrating")

                    adc_channel_0 = event.dl0.tel[tel_id].adc_sums[0]      # TODO
                    adc_channel_1 = event.dl0.tel[tel_id].adc_sums[1]      # TODO
                    uncalibrated_image = np.array([adc_channel_0, adc_channel_1])

                    calibrated_image = mc_calibration.apply_mc_calibration(uncalibrated_image, tel_id)

                    print("cropping ADC image")

                    cropped_img = geom_converter.astry_to_2d_array(calibrated_image)

                    # GET AND CROP THE PHOTOELECTRON IMAGE ####################

                    pe_image = event.mc.tel[tel_id].photo_electrons   # 1D np array

                    print("cropping PE image")

                    cropped_pe_img = geom_converter.astry_to_2d_array(pe_image)

                    # SAVE THE IMAGE ##########################################

                    output_file_path_template = "{}_TEL{:03d}_EV{:05d}.fits"

                    if output_directory is not None:
                        simtel_basename = os.path.basename(simtel_file_path)
                        prefix = os.path.join(output_directory, simtel_basename)
                    else:
                        prefix = simtel_file_path

                    output_file_path = output_file_path_template.format(prefix,
                                                                        tel_id,
                                                                        event_id)

                    print("saving", output_file_path)

                    metadata = {}
                    metadata['tel_id'] = tel_id
                    metadata['foclen'] = quantity_to_tuple(event.meta.optical_foclen[tel_id], 'm')
                    metadata['event_id'] = event_id
                    metadata['mc_e'] =  quantity_to_tuple(event.mc.energy, 'TeV')
                    metadata['mc_az'] = quantity_to_tuple(event.mc.az, 'rad')
                    metadata['mc_alt'] = quantity_to_tuple(event.mc.alt, 'rad')
                    metadata['mc_corex'] = quantity_to_tuple(event.mc.core_x, 'm')
                    metadata['mc_corey'] = quantity_to_tuple(event.mc.core_y, 'm')

                    save_fits(cropped_img, cropped_pe_img, output_file_path, metadata)


def quantity_to_tuple(quantity, unit_str):
    """
    Splits a quantity into a tuple of (value,unit) where unit is FITS complient.

    Useful to write FITS header keywords with units in a comment.

    Parameters
    ----------
    quantity : astropy quantity
        The Astropy quantity to split.
    unit_str: str
        Unit string representation readable by astropy.units (e.g. 'm', 'TeV', ...)

    Returns
    -------
    tuple
        A tuple containing the value and the quantity.
    """
    return quantity.to(unit_str).value, quantity.to(unit_str).unit.to_string(format='FITS')


def save_fits(img, pe_img, output_file_path, metadata):
    """
    Write a FITS file containing pe_img, output_file_path and metadata.

    Parameters
    ----------
    img: ndarray
        The "input image" to save (it should be a 2D Numpy array).
    pe_img: ndarray
        The "reference image" to save (it should be a 2D Numpy array).
    output_file_path: str
        The path of the output FITS file.
    metadata: tuple
        A dictionary containing all metadata to write in the FITS file.
    """

    if img.ndim != 2:
        raise Exception("The input image should be a 2D numpy array.")

    if pe_img.ndim != 2:
        raise Exception("The input image should be a 2D numpy array.")

    # http://docs.astropy.org/en/stable/io/fits/appendix/faq.html#how-do-i-create-a-multi-extension-fits-file-from-scratch
    hdu0 = fits.PrimaryHDU(img)
    hdu1 = fits.ImageHDU(pe_img)

    for key, val in metadata.items():
        if type(val) is tuple :
            hdu0.header[key] = val[0]
            hdu0.header.comments[key] = val[1]
        else:
            hdu0.header[key] = val

    if os.path.isfile(output_file_path):
        os.remove(output_file_path)

    hdu_list = fits.HDUList([hdu0, hdu1])

    hdu_list.writeto(output_file_path)



def main():

    # PARSE OPTIONS ###########################################################

    desc = "Generate FITS files compliant for cleaning benchmark (from simtel files)."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("--telescope", "-t",
                        metavar="INTEGER LIST",
                        help="The telescopes to query (telescopes number separated by a comma)")

    parser.add_argument("--event", "-e",
                        metavar="INTEGER LIST",
                        help="The events to extract (events ID separated by a comma)")

    parser.add_argument("--output", "-o",
                        metavar="DIRECTORY",
                        help="The output directory")

    parser.add_argument("fileargs", nargs="+", metavar="FILE",
                        help="The simtel files to process")

    args = parser.parse_args()

    if args.telescope is None:
        tel_id_filter_list = DEFAULT_TEL_FILTER
    else:
        tel_id_filter_list = [int(tel_id_str) for tel_id_str in args.telescope.split(",")]

    if args.event is None:
        event_id_filter_list = None
    else:
        event_id_filter_list = [int(event_id_str) for event_id_str in args.event.split(",")]

    print("Telescopes:", tel_id_filter_list)
    print("Events:", event_id_filter_list)

    output_directory = args.output
    simtel_file_path_list = args.fileargs

    if output_directory is not None:
        if not (os.path.exists(output_directory) and os.path.isdir(output_directory)):
            raise Exception("{} does not exist or is not a directory.".format(output_directory))

    # ITERATE OVER SIMTEL FILES ###############################################

    for simtel_file_path in simtel_file_path_list:

        print("Processing", simtel_file_path)

        # EXTRACT, CROP AND SAVE THE IMAGES ###################################

        extract_images(simtel_file_path, tel_id_filter_list, event_id_filter_list, output_directory)


if __name__ == "__main__":
    main()

