Example 7
=========

Example 7 shows how **pyrecodes** simulates socio-technical regional recovery by coupling physical infrastructure recovery with LLM-driven household decision-making. The case study is a subset of Alameda Island, California, subjected to earthquake damage. Technical systems include residential buildings and the water supply system. Social systems are modelled as household generative agents that decide where to stay as recovery progresses. The simulation uses a weekly time step.

Running the example
-------------------

Example 7 Jupyter notebook illustrates how to run the socio-technical recovery simulation, visualize household location dynamics over time, and plot the post-disaster supply/demand dynamics for shelter and potable water.

.. hint::

    By default, the notebook runs the simulation with no additional prompting strategy. Three prompting strategies are available, each with a corresponding main configuration file: ``SmallAlameda_Main.json`` (baseline GPT), ``SmallAlameda_Main_Literature.json`` (literature-informed), and ``SmallAlameda_Main_Ruleset.json`` (ruleset-constrained).

.. note::

    Running this example requires an OpenAI API key provided in an ``openai_api_key.json`` file in the root of the repository in the format ``{"API_KEY": "your-key-here"}``.

The example can be run locally by downloading the `Example 7 Jupyter notebook <https://github.com/NikolaBlagojevic/pyrecodes/blob/main/Example7_SocioTechnicalRecoveryWithGenerativeAgents.ipynb>`_ and the required files from the `Example 7 folder <https://github.com/NikolaBlagojevic/pyrecodes/tree/main/Example%207>`_.

Technical systems
-----------------

The technical systems modelled in Example 7 are:

- **Residential buildings**: provide shelter to households. Building damage states are derived from R2DTool's probabilistic hazard assessment. Buildings recover over time through repair activities conditioned on their initial damage state and the availability of recovery resources.
- **Water supply system**: distributes potable water to households. Water distribution is simulated using `REWET <https://doi.org/10.1061/JITSE4.ISENG-2427>`_. Water demand changes as households leave damaged buildings and return when buildings are repaired.
- **Neighboring town**: represents an out-of-town destination for displaced households.

Household generative agents
---------------------------

Each household is modelled as a generative agent implemented in the ``HouseholdGPT`` class. At each weekly time step, an agent receives a narrative describing its current situation — including the time since the disaster, its current location, building damage, access to potable water, and the behavior of neighboring households — and decides where to stay. Available options depend on the household's current location:

- **At home**: ``StayAtHome``, ``LeaveTown``, or ``MoveToFriend_ID``
- **With a friend**: ``StayWithFriend_ID``, ``ReturnHome``, ``LeaveTown``, or ``MoveToFriend_ID``
- **Out of town**: ``StayOutOfTown`` or ``ReturnHome``

Each agent is initialized with socio-economic characteristics — tenure, income, number of occupants, children, elderly, employment status, immigration status, and the number of friends in town — which condition its decision-making throughout the simulation.

Household decisions feed back into the simulation: the number of occupants at each building at each time step determines the demand for shelter and potable water, coupling human mobility with infrastructure recovery dynamics.

Prompting strategies
--------------------

Three prompting strategies are available, selected by choosing the corresponding main configuration file:

- ``SmallAlameda_Main.json`` — baseline GPT with no additional guidance.
- ``SmallAlameda_Main_Literature.json`` — agents are informed by summaries of relevant academic literature on household post-disaster displacement.
- ``SmallAlameda_Main_Ruleset.json`` — agents are constrained by a decision ruleset derived from the literature.

Results
-------

The notebook plots the number of households in town over time, the met demand for shelter and potable water at each building, and geo-visualizations of household locations at selected time steps.
