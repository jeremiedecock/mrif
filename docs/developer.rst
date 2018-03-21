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

.. The following guidline is mostly taken from https://cta-observatory.github.io/ctapipe/_sources/getting_started/index.rst.txt

Step 1: Set up your package environment
+++++++++++++++++++++++++++++++++++++++

.. TODO: make a short introduction to explain what is a virtual environment and why it is recommanded to use it

.. TODO: explain the same things with the native venv alternative

In your terminal, change to the directory where you cloned `pywi`, and type::

    conda env create -f environment.yml

This will create a conda virtual environment called `pywi-dev` with all
the PyWI dependencies and a few useful packages for development and
interaction.

If you want to give a different name to this environment, replace the previous
command by::

    conda env create -n NAME_OF_THE_ENVIROMENT -f environment.yml

and don't forget to adapt the following commands.

You can check the virtual environment has been successfully
created with the following command::

    conda env list

Next, switch to this new virtual environment:

* On Windows, in your Anaconda Prompt, run ``activate pywi-dev``
* On MacOSX and Linux, in your Terminal, run ``source activate pywi-dev``

You will need to type that last command any time you open a new
terminal to activate the virtual environment (you can of course
install everything into the base Anaconda environment without creating
a virtual environment, but then you may have trouble if you want to
install other packages with different requirements on the
dependencies).

If you want to see the list of packages installed in the virtual environment,
type::

    conda list -n pywi-dev

If later you want to leave the `pywi-dev` virtual environment:

* On Windows, in your Anaconda Prompt, run ``deactivate``
* On MacOSX and Linux, in your Terminal, run ``source deactivate``

Also if you want to completely remove this environment from your system, you
can type::

    conda remove --name pywi-dev --all

See https://conda.io/docs/user-guide/tasks/manage-environments.html for more
information on Anaconda virtual environments.

Step 2: Setup PyWI for development
++++++++++++++++++++++++++++++++++

Now setup this cloned version for development. The following command
will make symlinks in your python library directory to your PyWI
installation (it creates a `.pth` file, there is no need to set
PYTHONPATH, in fact it should be blank to avoid other problems). From
then on, all the PyWI binaries and the library itself will be
usable from anywhere.

For Linux/MacOSX users, type::

    python3 setup.py develop

or as a shorter alternative::

    make develop

For Windows users, type::

    py setup.py develop

If you want to remove the

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
