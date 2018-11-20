
#!/usr/bin/env python3
# coding: utf-8

"""
========================================
Denoising images using Starlet Transform
========================================

This example show how to denoise an image using the Starlet transform.
"""

###############################################################################
# Import required packages

import numpy as np
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
# Add noise

LAMBDA = 3
MU = 0.
SIGMA = 10.

noised_img = img + np.random.poisson(lam=LAMBDA, size=img.shape) + np.random.normal(loc=MU, scale=SIGMA, size=img.shape)

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(noised_img, cmap="gray")
plt.show()

###############################################################################
# Compute the wavelet transform

wt_imgs = starlet.wavelet_transform(noised_img, number_of_scales=4)

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

for i in range(len(wt_imgs)):
    print("scale", i, ":", wt_imgs[i].flatten().sum())

###############################################################################
# Filter wavelet coefficients

cleaned_img = pywi.processing.compositing.filter_with_starlet.clean_image(noised_img,
                                                                          filter_thresholds=[100., 0., 0.])


###############################################################################
# Plot the cleaned image

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(cleaned_img, cmap="gray")
plt.show()
