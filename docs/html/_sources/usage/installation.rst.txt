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

Adds dependencies for REWET (water network simulation) and the residual demand traffic simulator (example 5). Requires Python x86_64 — see the note below.

.. code-block:: bash

    pip install "pyrecodes[third_party_models]"

**Option 4 — Full installation**

Installs all optional dependencies.

.. code-block:: bash

    pip install "pyrecodes[household,third_party_models]"

.. note::

    Python x86_64 is required for the third-party infrastructure simulators used in Example 5. Further instructions are available `here <https://nheri-simcenter.github.io/R2D-Documentation/common/user_manual/installation/desktop/install_macOS.html>`_.

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

All examples are Jupyter notebooks and can be run locally.

To verify your installation, run Example 1 as described on the Examples page.
