Example 7
=========

Example 7 shows how **pyrecodes** simulates socio-technical regional recovery by coupling physical infrastructure recovery with LLM-driven household decision-making. The case study is a subset of Alameda Island, California, subjected to earthquake damage. Technical systems include residential buildings and the water supply system. Social systems are modelled as household generative agents that decide where to stay as recovery progresses. The simulation uses a weekly time step.

Running the example
-------------------

Example 7 Jupyter notebook illustrates how to run the socio-technical recovery simulation, visualize household location dynamics over time, and plot the post-disaster supply/demand dynamics for shelter and potable water.

.. hint::

    By default, the notebook runs the simulation with no additional prompting strategy. Three prompting strategies are available, each with a corresponding main configuration file: ``SmallAlameda_Main.json`` (baseline GPT), ``SmallAlameda_Main_Literature.json`` (literature-informed), and ``SmallAlameda_Main_Ruleset.json`` (ruleset-constrained).

.. note::

    Example 7 requires both the ``household`` and ``third_party_models`` extras, **x86_64 Python** (for REWET), and an OpenAI API key:

    .. code-block:: bash

        pip install "pyrecodes[household,third_party_models]"

    ``wntrfr`` and ``pandana`` provide pre-built wheels only for x86_64. On macOS with Apple Silicon, use the x86_64 Python installer from `python.org <https://www.python.org/downloads/>`_ (runs under Rosetta 2), or a conda x86_64 environment::

        CONDA_SUBDIR=osx-64 conda create -n pyrecodes_env python=3.9
        conda activate pyrecodes_env
        pip install "pyrecodes[household,third_party_models]"

    Provide your OpenAI API key in an ``openai_api_key.json`` file in the repository root: ``{"API_KEY": "your-key-here"}``.

    The notebook must be run from the **repository root folder**.

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

.. note::

    The example notebook runs the simulation with **6 households** (out of ~100 in the TAZ 964 dataset) to reduce computational cost. To run the full simulation, increase ``MaxNumHouseholds`` in the system configuration files (e.g. ``SmallAlameda_SystemConfiguration.json``). To speed up the simulation, set ``ASYNC_MODE = True`` in ``pyrecodes/household/household_gpt_base.py`` — this enables concurrent LLM calls for all households at each time step.

The figure below shows the number of households at each location (at home, with a friend, or out of town) over the 50-week simulation. After the earthquake, most households leave their damaged homes. As buildings are repaired and potable water is restored, households gradually return.

.. figure:: /figures/example_7_household_location_over_time.png
   :alt: Household location over time
   :align: center
   :width: 80%

   Number of households at each location over time.

The animation below shows the spatial distribution of household occupancy over the recovery period. Each building is colored according to occupancy: green indicates occupied buildings and red indicates vacant buildings. As buildings are repaired and water service is restored, households return and buildings transition from red to green.

.. figure:: /figures/example_7_household_recovery.gif
   :alt: Household recovery animation
   :align: center
   :width: 80%

   Animated geo-visualization of household locations during recovery.

Comparison across prompting strategies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The figure below compares household location dynamics across all four agent prompting strategies. Each panel shows the stacked area plot of households at home, with a friend, or out of town over the recovery period. The baseline and GPT-5 Mini agents show similar recovery trajectories, while the literature-informed and ruleset-constrained agents produce distinct displacement and return patterns shaped by their additional guidance.

.. figure:: /figures/example_7_household_movement_combined.png
   :alt: Household movement comparison across prompting strategies
   :align: center
   :width: 100%

   Household location dynamics for (a) baseline, (b) ruleset-constrained, (c) literature-informed, and (d) GPT-5 Mini agents.

Chat history
^^^^^^^^^^^^

The notebook prints the full LLM chat history for a selected household. The excerpt below shows how the agent is initialized with context and socioeconomic characteristics, and then makes weekly relocation decisions as the recovery progresses:

.. code-block:: text

    --- SYSTEM ---
    # Context:
     - You are a household in a city hit by an earthquake.
     - In the following your household socioeconomic characteristics will be
    provided first, followed by a description of your situation at different
    times during city's recovery.
     - Based on your socioeconomic characteristics and your current situation
    you need to inform us about your needs and decisions on where to stay in
    the future as the recovery progresses.
     Instructions:
    - You must behave consistently across time steps.
     - Your preferences and constraints do not change unless explicitly stated.

    --- SYSTEM ---
    Socioeconomic characteristics of your household:
     - You are Owner of the building you live in.
     - Your household income level is High.
     - There are 4 people in your household. Out of those 0 are children and
    4 are elderly.
     - 1 of household members are employed.
     - Your immigration status is foreign born.
     - You have 2 friends in this town.

    --- SYSTEM ---
     # Resource needs of the household:
     - These are the average per person resource needs for your household:
    {'PotableWater': 1050}. Take them into account when assessing the needs
    of the entire household.

    --- USER ---
     Your current situation:
     - It's now 1 weeks after the disaster.
     - You are currently staying at home.
     - Your friend with ID 1 is not in their home.
     - Your friend with ID 2 is not in their home.
     - All households are still in your neighborhood.
     - At your current location, your needs for Shelter are not satisfied.
     - At your current location, your needs for PotableWater are not satisfied.

     Task:
     Based on the current situation described above, choose where to stay
    tomorrow: StayAtHome, LeaveTown, MoveToFriend_1, MoveToFriend_2.

    --- ASSISTANT ---
    Relevant facts influencing my decision:
    1. It has been one week since the earthquake, and my household's needs
    for shelter and potable water are not being satisfied at home.
    2. Both of my friends are currently not at their homes, meaning I cannot
    seek shelter there at this moment.
    3. Leaving town would disconnect us from local resources and support
    networks, including potential housing assistance.

    Reasoning: Given the dire situation of lacking both shelter and potable
    water at my current home, it is essential to find a better living
    arrangement. Since my friends are not at their homes, moving to either
    of their places is not an option right now. Staying at home is not
    feasible due to the unmet basic needs. Therefore, the most reasonable
    decision is to leave town temporarily until I can ensure proper shelter
    and supplies for my household.

    LeaveTown

    --- USER ---
     Your current situation:
     - It's now 2 weeks after the disaster.
     - You are currently staying out of town.
     - Your friend with ID 1 is not in their home.
     - Your friend with ID 2 is not in their home.
     - The building where you lived before the disaster is completely damaged.
     - No households remain in your original neighborhood.
     - At your current location, your needs for Shelter are completely satisfied.
     - At your current location, your needs for PotableWater are completely
    satisfied.
    Your past experience:
     - Week 1: I am leaving town temporarily due to unmet needs for shelter
    and potable water at home, and with my friends currently unavailable
    for support.

     Task:
     Based on the current situation described above, choose where to stay
    tomorrow: ReturnHome, StayOutOfTown, MoveToFriend_1, MoveToFriend_2.

    --- ASSISTANT ---
    Relevant facts influencing my decision:
    1. My building has been completely damaged, and no households remain in
    my original neighborhood.
    2. I am out of town, where my needs for shelter and potable water are
    fully satisfied.
    3. My friends are unavailable; I cannot move to either of their
    residences as they are not in their homes.

    Reasoning: Given that my building is completely damaged and those who I
    might have turned to for support are currently unavailable, returning
    home is not an option as it is uninhabitable. Remaining out of town
    where my needs are satisfied is the most viable decision.

    StayOutOfTown

    --- USER ---
     Your current situation:
     - It's now 5 weeks after the disaster.
     - You are currently staying out of town.
     - Your friend with ID 1 is back in their home.
     - Your friend with ID 2 is not in their home.
     - The building where you lived before the disaster is still damaged.
     - Some households have returned to your original neighborhood.
     - At your current location, your needs for Shelter are completely satisfied.
     - At your current location, your needs for PotableWater are completely
    satisfied.
    Your past experience:
     - Weeks 1-4: Staying out of town because my building is completely
    damaged and basic needs were unmet at home.

     Task:
     Based on the current situation described above, choose where to stay
    tomorrow: ReturnHome, StayOutOfTown, MoveToFriend_1, MoveToFriend_2.

    --- ASSISTANT ---
    Relevant facts influencing my decision:
    1. My building is still damaged, so returning home is not yet viable.
    2. Friend 1 is back in their home and could potentially host us.
    3. Some neighbors have returned, suggesting partial recovery in the area.

    Reasoning: Although my building remains damaged, friend 1 has returned
    home. Moving to their place would bring me closer to my neighborhood
    and allow me to monitor the repair progress on my building. As an
    owner, I want to be nearby when repairs are completed.

    MoveToFriend_1
