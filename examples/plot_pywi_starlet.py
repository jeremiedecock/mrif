#!/usr/bin/env python3
# coding: utf-8

"""
===========================
PyWI Starlet Transform Demo
===========================

This example show how to transform an image using the Starlet transform.
"""

###############################################################################
# Import required packages

import matplotlib.pyplot as plt

import pywi
print(pywi.__version__)

from pywi.processing.transform import starlet

###############################################################################
# Get an image

import pywi.data

img = pywi.data.galaxy()

###############################################################################
# Plot the original image

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(img, cmap="gray")
plt.show()

###############################################################################
# Compute the wavelet transform

wt_imgs = starlet.wavelet_transform(img, number_of_scales=4)

###############################################################################
# Plot the wavelet transform coefficients

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))

ax1.imshow(wt_imgs[0], cmap="gray")
ax2.imshow(wt_imgs[1], cmap="gray")
ax3.imshow(wt_imgs[2], cmap="gray")
ax4.imshow(wt_imgs[3], cmap="gray")

plt.tight_layout()

plt.show()

###############################################################################
# Plot the wavelet transform coefficients histograms

fig, ax = plt.subplots(figsize=(12, 8))
ax.hist(img.flatten(), bins=50)
plt.show()

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
    
ax1.hist(wt_imgs[0].flatten(), bins=50)
ax2.hist(wt_imgs[1].flatten(), bins=50)
ax3.hist(wt_imgs[2].flatten(), bins=50)
ax4.hist(wt_imgs[3].flatten(), bins=50)

plt.show()
