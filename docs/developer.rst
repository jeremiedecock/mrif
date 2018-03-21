.. currentmodule:: pywi

=================
Developer's notes
=================

Source code
~~~~~~~~~~~

The source code is currently `available on GitHub`_ under the terms and
conditions of the `MIT license`_. Fork away!


Getting Started For Developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   the following guide is used only if you want to *develop* the
   `pywi` package. If you just want to write code that uses it
   externally, you should rather install it as explained
   :ref:`there <introduction_section>`.

This guide assumes you are using the *Anaconda* Python distribution,
installed locally (*miniconda* should also work).


Bug reports
~~~~~~~~~~~

To search for bugs or report them, please use the Bug Tracker at:

    https://github.com/jeremiedecock/pywi/issues



Contribute
~~~~~~~~~~

This project is written for Python 3.x. Python 2.x is *not* supported.

The `TODO.md`_ file contains the TODO list.

All contributions should at least comply with the following PEPs_:

- PEP8_ "Python's good practices"
- PEP257_ "Docstring Conventions"
- PEP287_ "reStructuredText Docstring Format"

All contribution should be properly documented and tested with unittest_
and/or doctest_.

The inline documentation (a.k.a. `docstrings <https://docs.python.org/3/glossary.html#term-docstring>`_)
should follow the `Numpy style <https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_
(check examples `here <http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html>`_).

pylint_, `pep8 <https://github.com/PyCQA/pep8>`__ and pyflakes_ should also be
used to check the quality of each module.


Changes
~~~~~~~

.. include:: ../CHANGES.rst
   :start-line: 2

.. _MIT license: https://opensource.org/licenses/MIT
.. _available on GitHub: https://github.com/jeremiedecock/pywi
.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _PEP257: https://www.python.org/dev/peps/pep-0257/
.. _PEP287: https://www.python.org/dev/peps/pep-0287/
.. _PEPs: https://www.python.org/dev/peps/
.. _unittest: https://docs.python.org/3/library/unittest.html
.. _doctest: https://docs.python.org/3/library/doctest.html
.. _pylint: http://www.pylint.org/
.. _pyflakes: https://pypi.python.org/pypi/pyflakes
.. _TODO.md: https://github.com/jeremiedecock/pywi/blob/master/TODO.md
