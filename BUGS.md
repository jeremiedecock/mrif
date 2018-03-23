# Known bugs

1. Following README.rst instructions to reinstall the library may cause the following issues:
   - "pip install --upgrade pywicta" will also upgrade external libraries like numpy, scipy, ... It's not desirable.
   - "pip install --upgrade pywicta --no-deps" does nothing...
   - So what command users should use to upgrade the library without touching external libraries ?
   - There may be issues with pip cache too during upgrade (users may have to use --no-cache-dir to force pip to check the latest version of the library on PyPI)
