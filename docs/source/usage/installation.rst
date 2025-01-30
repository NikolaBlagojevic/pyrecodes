Installing pyrecodes
====================

The prerequisite for installing pyrecodes is having Python version 3.9.6 installed on your machine.

The simplest way to install pyrecodes is to use `pip`:

.. code-block:: Python

    pip install pyrecodes

pyrecodes can also be installed by `cloning <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`_ the source code available on `Github <https://github.com/NikolaBlagojevic/pyrecodes/tree/main>`_.

It's good practice to use a virtual environment when installing pyrecodes to keep its dependencies isolated from other Python projects on your machine. The repository includes a requirements.txt file in the root directory, which allows you to install all dependencies at once.

.. code-block:: Python

    pip install -r requirements.txt

.. note::

    Please note that python version x86_64 is required to run the third-party infrastructure simulators presented in Example 5. Further instructions are available `here <https://nheri-simcenter.github.io/R2D-Documentation/common/user_manual/installation/desktop/install_macOS.html>`_


Running Examples
----------------

To ensure that the installation is successful, please run Example 1 as specified in the Examples page.

All examples are written as Jupyter notebooks and can be run locally or online using Google Colab. More information on installing Jupyter notebooks can be found `here <https://jupyter.org/install>`_.  


.. Dependencies
.. ------------

.. Apart from the Python's standard library, pyrecodes relies on several external packages:
..  - numpy
..  - pandas
..  - geopandas
..  - shapely
..  - contextily (for visualization only)
..  - matplotlib (for visualization only)
..  - imageio (for visualization only)

.. These packages, along with their dependencies, define the requirements of the pyrecodes library.



