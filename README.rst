=============================
PyWI - Python Wavelet Imaging
=============================

Copyright (c) 2016-2018 Jeremie DECOCK (www.jdhp.org)

* Online documentation: https://jeremiedecock.github.io/pywi/
* Source code: https://github.com/jeremiedecock/pywi
* Issue tracker: https://github.com/jeremiedecock/pywi/issues
* PyWI on PyPI: https://pypi.org/project/pywi/

.. Former documentation: http://sap-cta-data-pipeline.readthedocs.io/en/latest/

Description
===========

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


Dependencies
============

* Python >= 3.0
* Numpy
* Scipy
* Scikit-image
* Astropy (fits package)
* _Cosmostat _iSAP Sparce2D

.. _install:

Installation
============

Gnu/Linux
---------

You can install, upgrade, uninstall PyWI with these commands (in a
terminal)::

    pip install --pre pywi
    pip install --upgrade pywi
    pip uninstall pywi

Or, if you have downloaded the PyWI source code::

    python3 setup.py install

.. There's also a package for Debian/Ubuntu::
.. 
..     sudo apt-get install pywi

Windows
-------

.. Note:
.. 
..     The following installation procedure has been tested to work with Python
..     3.4 under Windows 7.
..     It should also work with recent Windows systems.

You can install, upgrade, uninstall PyWI with these commands (in a
`command prompt`_)::

    py -m pip install --pre pywi
    py -m pip install --upgrade pywi
    py -m pip uninstall pywi

Or, if you have downloaded the PyWI source code::

    py setup.py install

MacOSX
-------

.. Note:
.. 
..     The following installation procedure has been tested to work with Python
..     3.5 under MacOSX 10.9 (*Mavericks*).
..     It should also work with recent MacOSX systems.

You can install, upgrade, uninstall PyWI with these commands (in a
terminal)::

    pip install --pre pywi
    pip install --upgrade pywi
    pip uninstall pywi

Or, if you have downloaded the PyWI source code::

    python3 setup.py install

Cosmostat iSAP Sparce2D installation
====================================

1. Download http://www.cosmostat.org/wp-content/uploads/2014/12/ISAP_V3.1.tgz (see http://www.cosmostat.org/software/isap/)
2. Unzip this archive, go to the "sparse2d" directory and compile the sparse2d
   library. It should generate two executables named ``mr_transform`` and ``mr_filter``::

    tar -xzvf ISAP_V3.1.tgz
    cd ISAP_V3.1/cxx
    tar -xzvf sparse2d_V1.1.tgz
    cd sparse2d
    compile the content of this directory

Example
=======

1. Download a sample image (`shower.fits <https://raw.githubusercontent.com/jdhp-misc/sample-images/master/shower.fits>`_)
2. In your system terminal, type::
  
    pywi-mrfilter shower.fits

3. Use the ``-h`` option for more options

A "benchmark mode" can also be used to clean images and assess cleaning
algorithms (it's still a bit experimental): use the additional option ``-b all``
in each command (and put several fits files in input e.g. ``\*.fits``)

Bug reports
===========

To search for bugs or report them, please use the PyWI Bug Tracker at:

    https://github.com/jeremiedecock/pywi/issues


.. _PyWI: https://github.com/jeremiedecock/pywi
.. _command prompt: https://en.wikipedia.org/wiki/Cmd.exe
.. _Cosmostat: http://www.cosmostat.org/
.. _iSAP: http://www.cosmostat.org/software/isap
