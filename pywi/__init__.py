"""Python Wavelet Imaging

PyWI is an image filtering library aimed at removing additive background noise
from raster graphics images.

* Input: a FITS file containing the raster graphics to clean (i.e. an image
  defined as a classic rectangular lattice of square pixels).
* Output: a FITS file containing the cleaned raster graphics.

The image filter relies on multiresolution analysis methods (Wavelet
transforms) that remove some scales (frequencies) locally in space. These
methods are particularly efficient when signal and noise are located at
different scales (or frequencies). Optional features improve the SNR ratio when
the (clean) signal constitute a single cluster of pixels on the image (e.g.
electromagnetic showers produced with Imaging Atmospheric Cherenkov
Telescopes). This library is written in Python and is based on the existing
Cosmostat tools iSAp (Interactive Sparse Astronomical data analysis Packages
http://www.cosmostat.org/software/isap/).

The PyWI library also contains a dedicated package to optimize the image filter
parameters for a given set of images (i.e. to adapt the filter to a specific
problem). From a given training set of images (containing pairs of noised and
clean images) and a given performance estimator (a function that assess the
image filter parameters comparing the cleaned image to the actual clean image),
the optimizer can determine the optimal filtering level for each scale.

The PyWI library contains:

* wavelet transform and wavelet filtering functions for image multiresolution
  analysis and filtering;
* additional filter to remove some image components (non-significant pixels
  clusters);
* a set of generic filtering performance estimators (MSE, NRMSE, SSIM, PSNR,
  image moment's difference), some relying on the scikit-image Python library
  (supplementary estimators can be easily added to meet particular needs);
* a graphical user interface to visualize the filtering process in the wavelet
  transformed space;
* an Evolution Strategies (ES) algorithm known in the mathematical optimization
  community for its good convergence rate on generic derivative-free continuous
  global optimization problems (Beyer, H. G. (2013) "The theory of evolution
  strategies", Springer Science & Business Media);
* additional tools to manage and monitor the parameter optimization.

Note:

    This project is in beta stage.

Viewing documentation using IPython
-----------------------------------
To see which functions are available in `pywi`, type ``pywi.<TAB>`` (where
``<TAB>`` refers to the TAB key), or use ``pywi.*transform*?<ENTER>`` (where
``<ENTER>`` refers to the ENTER key) to narrow down the list.  To view the
docstring for a function, use ``pywi.transform?<ENTER>`` (to view the
docstring) and ``pywi.transform??<ENTER>`` (to view the source code).
"""

# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
# X.Y
# X.Y.Z # For bugfix releases
#
# Admissible pre-release markers:
# X.YaN # Alpha release
# X.YbN # Beta release
# X.YrcN # Release Candidate
# X.Y # Final release
#
# Dev branch marker is: 'X.Y.dev' or 'X.Y.devN' where N is an integer.
# 'X.Y.dev0' is the canonical version of 'X.Y.dev'

__version__ = '0.3.dev1'

def get_version():
    return __version__

# The following lines are temporary commented to avoid BUG#2 (c.f. BUGS.md)
#from . import benchmark
#from . import io
#from . import optimization
#from . import processing
#from . import ui
