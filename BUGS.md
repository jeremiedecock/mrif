# Known bugs

1. Following README.rst instructions to reinstall the library may cause the following issues:
   - "pip install --upgrade pywicta" will also upgrade external libraries like numpy, scipy, ... It's not desirable.
   - "pip install --upgrade pywicta --no-deps" does nothing...
   - So what command users should use to upgrade the library without touching external libraries ?
   - There may be issues with pip cache too during upgrade (users may have to use --no-cache-dir to force pip to check the latest version of the library on PyPI)
2. The following error happen in Travis CI (caused by the use of "from . import benchmark" in "pywi/__init__.py"):

    $ pip install pywi
    Collecting pywi
    Downloading pywi-0.1.dev17.tar.gz (74kB)
    100% |████████████████████████████████| 81kB 4.3MB/s 
    Complete output from command python setup.py egg_info:
    Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "/tmp/pip-build-av28zfd9/pywi/setup.py", line 47, in <module>
    from pywi import get_version
    File "/tmp/pip-build-av28zfd9/pywi/pywi/__init__.py", line 78, in <module>
    from . import benchmark
    File "/tmp/pip-build-av28zfd9/pywi/pywi/benchmark/__init__.py", line 6, in <module>
    from . import assess
    File "/tmp/pip-build-av28zfd9/pywi/pywi/benchmark/assess.py", line 40, in <module>
    from pywi.image.pixel_clusters import kill_isolated_pixels
    File "/tmp/pip-build-av28zfd9/pywi/pywi/image/__init__.py", line 6, in <module>
    from . import pixel_clusters
    File "/tmp/pip-build-av28zfd9/pywi/pywi/image/pixel_clusters.py", line 29, in <module>
    import scipy.ndimage as ndimage
    ModuleNotFoundError: No module named 'scipy'


