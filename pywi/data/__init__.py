"""Data modules

This package contains image examples used in tutorials and notebooks.
"""

import numpy as np

def camera():
    """Gray-level "galaxy" image.

    Often used for tutorials and examples.

    This is the Whirlpool Galaxy, also known as M51 or NGC 5194.

    Credits: NASA and The Hubble Heritage Team (STScI/AURA), 5 April 2001.

    Copyright
    ---------

    This file is in the public domain because it was created by NASA
    and ESA. NASA Hubble material (and ESA Hubble material prior to 2009) is
    copyright-free and may be freely used as in the public domain without fee,
    on the condition that only NASA, STScI, and/or ESA is credited as the
    source of the material.

    (https://commons.wikimedia.org/wiki/File:Whirpool_Galaxy.jpg)

    Sources
    -------

    - http://hubblesite.org/image/1038/news_release/2001-10
    - https://commons.wikimedia.org/wiki/File:Whirpool_Galaxy.jpg

    Returns
    -------
    camera : (256, 256) uint8 ndarray
        Galaxy image.
    """
    return np.load("galaxy.npy")
