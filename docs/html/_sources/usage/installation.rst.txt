Installing pyrecodes
====================

pyrecodes requires Python 3.9 or later.

Installation options
--------------------

**Option 1 — Core only (default)**

Installs pyrecodes with all dependencies needed for the core simulation framework, visualization, and examples 1–4.

.. code-block:: bash

    pip install pyrecodes

**Option 2 — With household / LLM agents**

Adds dependencies for the GPT-driven household generative agents (examples 6–7). Requires an OpenAI API key.

.. code-block:: bash

    pip install "pyrecodes[household]"

**Option 3 — With third-party infrastructure simulators**

Adds dependencies for REWET (water network simulation) and the residual demand traffic simulator (example 5).

.. code-block:: bash

    pip install "pyrecodes[third_party_models]"

**Option 4 — Full installation (example 7)**

Example 7 couples LLM household agents with REWET water simulation and requires both extras:

.. code-block:: bash

    pip install "pyrecodes[household,third_party_models]"

.. warning::

    **x86_64 Python required for** ``third_party_models`` **.**
    ``wntrfr`` and ``pandana`` provide pre-built wheels only for x86_64 and cannot be compiled from source on Apple Silicon (arm64) or macOS 15+ due to missing C++ standard library headers in CommandLineTools.

    On macOS, use the x86_64 Python installer from `python.org <https://www.python.org/downloads/>`_ (the *macOS 64-bit universal2 and Intel installer*), which runs under Rosetta 2.
    Alternatively, use `conda <https://docs.conda.io/en/latest/>`_ with an x86_64 environment::

        CONDA_SUBDIR=osx-64 conda create -n pyrecodes_env python=3.9
        conda activate pyrecodes_env
        pip install "pyrecodes[household,third_party_models]"

    Further setup instructions are available `here <https://nheri-simcenter.github.io/R2D-Documentation/common/user_manual/installation/desktop/install_macOS.html>`_.

.. note::

    ``third_party_models`` requires ``numpy<2`` due to a ``pandana`` binary compatibility constraint. This is handled automatically by pip.

Installing from source
----------------------

Clone the repository and install in editable mode:

.. code-block:: bash

    git clone https://github.com/NikolaBlagojevic/pyrecodes.git
    cd pyrecodes
    pip install -e .

To include optional dependencies:

.. code-block:: bash

    pip install -e ".[household]"
    pip install -e ".[third_party_models]"
    pip install -e ".[household,third_party_models]"

It is good practice to use a virtual environment to keep pyrecodes dependencies isolated from other projects:

.. code-block:: bash

    python -m venv env_pyrecodes
    source env_pyrecodes/bin/activate      # macOS / Linux
    env_pyrecodes\\Scripts\\activate         # Windows
    pip install -e ".[household,third_party_models]"

Running Examples
----------------

All examples are Jupyter notebooks. Download or clone the repository, then run notebooks from the **repository root folder**. Both ``main.run()`` and the example notebooks resolve input files using paths relative to the repository root, so running from a different directory will cause file-not-found errors.

.. code-block:: bash

    git clone https://github.com/NikolaBlagojevic/pyrecodes.git
    cd pyrecodes
    jupyter notebook

To verify your installation, run Example 1 as described on the Examples page.
