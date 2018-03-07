===================================
MRIF - MultiResolution Image Filter
===================================

Copyright (c) 2016,2017,2018 Jeremie DECOCK (www.jdhp.org) and Tino Michael

* Online documentation: https://jeremiedecock.github.io/mrif/
* Source code: https://github.com/jeremiedecock/mrif
* Issue tracker: https://github.com/jeremiedecock/mrif/issues
* MRIF on PyPI: https://pypi.org/project/mrif/

.. Former documentation: http://sap-cta-data-pipeline.readthedocs.io/en/latest/

Description
===========

Signal processing for gamma-ray science.

Note:

    This project is in beta stage.


Dependencies
============

*  Python >= 3.0

.. _install:

Installation
============

Gnu/Linux
---------

You can install, upgrade, uninstall MRIF with these commands (in a
terminal)::

    pip install --pre mrif
    pip install --upgrade mrif
    pip uninstall mrif

Or, if you have downloaded the MRIF source code::

    python3 setup.py install

.. There's also a package for Debian/Ubuntu::
.. 
..     sudo apt-get install mrif

Windows
-------

.. Note:
.. 
..     The following installation procedure has been tested to work with Python
..     3.4 under Windows 7.
..     It should also work with recent Windows systems.

You can install, upgrade, uninstall MRIF with these commands (in a
`command prompt`_)::

    py -m pip install --pre mrif
    py -m pip install --upgrade mrif
    py -m pip uninstall mrif

Or, if you have downloaded the MRIF source code::

    py setup.py install

MacOSX
-------

.. Note:
.. 
..     The following installation procedure has been tested to work with Python
..     3.5 under MacOSX 10.9 (*Mavericks*).
..     It should also work with recent MacOSX systems.

You can install, upgrade, uninstall MRIF with these commands (in a
terminal)::

    pip install --pre mrif
    pip install --upgrade mrif
    pip uninstall mrif

Or, if you have downloaded the MRIF source code::

    python3 setup.py install

Image cleaning guidelines
=========================

Here is the basic guidelines to clean images (and assess cleaning algorithms).

Step 1
------

Install mr_transform and mr_filter (the cosmostat wavelet transform and filter tools):

1. download http://www.cosmostat.org/wp-content/uploads/2014/12/ISAP_V3.1.tgz (see http://www.cosmostat.org/software/isap/)
2. unzip this archive, go to the "sparse2d" directory and compile the sparse2d
   library. It should generate an executable named "mr_transform"::

    tar -xzvf ISAP_V3.1.tgz
    cd ISAP_V3.1/cxx
    tar -xzvf sparse2d_V1.1.tgz
    cd sparse2d
    compile the content of this directory

Step 2
------

Clean images:

1. to filter one fits file:

   - with FFT : in data-pipeline-standalone-scripts, run ``./mrif/denoising/fft.py -s -t 0.02 FITS_FILE`` (-t = threshold in the Fourier space, use the -h option to see command usage)
   - with Wavelets : in data-pipeline-standalone-scripts, run ``./mrif/denoising/wavelets_mrtrransform.py FITS_FILE`` (use the -h option to see command usage)

2. instead of the step 2.1, the "benchmark mode" can be set to clean
   images and assess cleaning algorithms (it's still a bit experimental) : use
   the same instructions than for step 2.1 with the additional option "-b 1" in
   each command (and put several fits files in input e.g. "\*.fits")

Bug reports
===========

To search for bugs or report them, please use the SAp Data Pipeline Standalone
Scripts Bug Tracker at:

    https://github.com/jeremiedecock/mrif/issues


.. _MRIF: https://github.com/jeremiedecock/mrif
.. _command prompt: https://en.wikipedia.org/wiki/Cmd.exe
