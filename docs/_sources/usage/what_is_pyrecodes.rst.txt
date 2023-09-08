What is pyrecodes?
==================

**pyrecodes** is an open-source object-oriented Python library for regional disaster recovery simulation and disaster resilience assessment of the built environment.

**pyrecodes** is based on the iRe-CoDeS framework developed in the research group of Professor Božidar Stojadinović at the `Chair of Structural Dynamics and Earthquake Engineering <https://stojadinovic.ibk.ethz.ch/>`_ at ETH Zurich, Switzerland. 

pyrecodes architecture
----------------------

Following figure represents the simplified object-oriented architecture of **pyrecodes**.

.. figure:: ../figures/simplified_pyrecodes_architecture.png
        :alt: Simplified architecture of pyrecodes.

        Simplified architecture of pyrecodes.

iRe-CoDeS framework
--------------------

The iRe-CoDeS framework discretizes a system into components and simulates the change in components' supply and demand for various resources over the post-disaster recovery period. Components' interaction is captured by simulating the flow of resources among components and conditioning their ability to operate and recover on their resource demand fulfillment. System's resilience is then assessed by contrasting the post-disaster system-level evolution of supply, demand and consumption of various resources and identifying the system's unmet demand.

.. figure:: ../figures/1slide_iRe-CoDeS.gif
        :alt: Overview of the iRe-CoDeS framework.

        Overview of the iRe-CoDeS framework.


The iRe-CoDeS framework has been used to:
 - capture cascading effects caused by interdependencies among infrastructure systems following a disaster `[link] <https://doi.org/10.1080/15732479.2022.2052912>`_

    .. figure:: ../figures/irecodes_SIE_paper_EP_plot.png
        :alt: Supply, demand and consumption of electric power after a scenario earthquake in the virtual community.

        Supply, demand and consumption of electric power after a scenario earthquake in the virtual community. Dashed lines represent supply/consumption dynamics withouth considering infrastructure interdependencies, while solid lines include interdependencies. Gray LoR area marks the unmet demand for electric power caused by infrastructure interdependencies.

 - conduct scenario-based seismic resilience assessment of a virtual community by integrating iRe-CoDeS with ground motion models and HAZUS fragility and recovery functions `[link] <https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/463555/1/7d-0003_Published.pdf>`_ 

    .. figure:: ../figures/irecodes_workflow.png
            :alt: Workflow of resilience assessment in iRe-CoDeS extends the traditional regional risk assessment by simulating recovery and quantifying resilience.

            Workflow of resilience assessment in iRe-CoDeS extends the traditional regional risk assessment by simulating recovery and quantifying resilience.

 - conduct probabilistic seismic resilience assessment of a virtual community and obtaining risk-based resilience metrics `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/463549>`_ 

    .. figure:: ../figures/17WCEE_LoR_LossCurves_CIS_1.png
            :alt: Probabilistic resilience assessment results in assessing the mean annual rate of exceeding a certain value of a Lack of Resilience (LoR) - the unmet demand for a resource, here electric power, during the resilience assessment period.

            Probabilistic resilience assessment results in assessing the mean annual rate of exceeding a certain value of a Lack of Resilience (LoR) - the unmet demand for a resource, here electric power, during the resilience assessment period.

 - quantify component importance for disaster resilience of a system using Sobol' indices and a heuristic upper and lower-bound search `[link] <https://www.sciencedirect.com/science/article/pii/S0951832022003702>`_ 

    .. figure:: ../figures/sobol_indices_EPSS.png
            :alt: Component importance ranking for the resilience of an electric power supply system.

            Component importance ranking for the resilience of an electric power supply system.

 - assess seismic resilience of an electrical substation `[link] <https://onlinelibrary.wiley.com/doi/pdf/10.1002/eqe.3800>`_

    .. figure:: ../figures/substation_resilience.png
            :alt: Resilience assessment of an electrical substation using the iRe-CoDeS framework.

            Resilience assessment of an electrical substation using the iRe-CoDeS framework.

 - evaluate NIST community resilience goals `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/586997>`_ 

    .. figure:: ../figures/irecodes_NIST_goals.png
            :alt: NIST resilience goals can be assessed using iRe-CoDeS by defining functionality of a system as the percent of met user demand for a resource provided by the considered system.

            NIST resilience goals can be assessed using iRe-CoDeS by defining functionality of a system as the percent of met user demand for a resource provided by the considered system.

 - assess housing resilience of a virtual community exposed to seismic hazard `[link] <https://ascelibrary.org/doi/abs/10.1061/9780784484432.082>`_

    .. figure:: ../figures/irecodes_housing_resilience_lifelines2021.png
            :alt: By treating housing as a resource provided by the building stock, iRe-CoDeS can assess housing resilience by looking at post-disaster housing supply/demand dynamics.

            By treating housing as a resource provided by the building stock, iRe-CoDeS can assess housing resilience by looking at post-disaster housing supply/demand dynamics.

 - assess the adequate post-disaster supply of recovery resources for the city of Kraljevo, Serbia to improve its seismic resilience `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/586957>`_ 

    .. figure:: ../figures/adequate_worker_supply_kraljevo.png
            :alt: Relation between recovery resource supply, in this case workers, and recovery time can be assessed using iRe-CoDeS.

            Relation between recovery resource supply, in this case workers, and recovery time can be assessed using iRe-CoDeS.


 - enable risk-informed resilience assessment using Lack of Resilience surfaces `[link] <https://www.researchgate.net/publication/363671446_Risk-Informed_Resilience_Assessment_of_Communities_using_Lack_of_Resilience_Surfaces>`_ 

     .. figure:: ../figures/lor_surface_example.png
            :alt: Example of an LoR surface.

            Example of an LoR surface showing the annual rate of exceeding a certain percent of unmet resource demand (i.e., the LoR) at each time step of the simulated recovery process.

 - compare the iRe-CoDeS seismic housing resilience assessment with a real-life post-earthquake recovery of the city of Kraljevo, Serbia `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/586954>`_ 

     .. figure:: ../figures/kraljevo_housing_resilience_validation.png
            :alt: Comparing the iRe-CoDeS seismic housing recovery estimates with the observed housing recovery data from the 2010 Kraljevo, Serbia, earthquake.

            Comparing the iRe-CoDeS seismic housing recovery estimates with the observed housing recovery data from the 2010 Kraljevo, Serbia, earthquake.

 - simulate recovery impeding factors and the effect of regional resource constraints on the recovery of San Francisco following a hypothetical earthquake `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/587004>`_

    .. figure:: ../figures/SF_HousingRecovery_small.gif
            :alt: Relation between recovery resource supply, in this case workers, and recovery time can be assessed using iRe-CoDeS.

            Relation between recovery resource supply, in this case workers, and recovery time can be assessed using iRe-CoDeS.

 - capture the impact of transportation infrastructure on community disaster resilience in a virtual community `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/527466>`_

     .. figure:: ../figures/transportation_infrastructure_community_resilience.png
            :alt: Post-disaster inoperability of the damaged transportation infrastructure prevents access to damaged components, delaying their repair and preventing the mobilization of available workers.

            Post-disaster inoperability of the damaged transportation infrastructure prevents access to damaged components, delaying their repair and preventing the mobilization of available workers.

 - integrate advanced building-component-level functional recovery modelling framework F-Rec with iRe-CoDeS `[link] <https://www.research-collection.ethz.ch/handle/20.500.11850/610946>`_

     .. figure:: ../figures/f-rec_irecodes_example.png
            :alt: By integrating F-Rec building-level recovery models into the regional iRe-CoDeS recovery model we capture recovery resource constraints on a building component level at each floor in the entire region.

            By integrating F-Rec building-level recovery models into the regional iRe-CoDeS recovery model we capture recovery resource constraints on a building component level at each floor in the entire region.

More information on the iRe-CoDeS framework can be found `here <https://www.research-collection.ethz.ch/handle/20.500.11850/605682>`_.




