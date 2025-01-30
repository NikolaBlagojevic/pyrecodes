from pyrecodes.component.component import Component

class DistributionListCreator:
    """
    Creates a list specifying the order of resource distribution in the system.

    This class determines the order in which resources should be distributed to capture components' interdependencies and calculate consumption.
    The resource order is fixed: Bridge Services, Transfer Services, Independent Resources, Interdependent Resources.

    Attributes:
        | components (list[Component]): A list of components in the system.
        | resources (dict): A dictionary containing resource parameters for the system.

    """

    def __init__(self, components: list[Component], resources: dict):
        """
        Initialize the DistributionListCreator with components and resources.

        Args:
            | components (list[Component]): A list of components in the system.
            | resources (dict): A dictionary containing resource parameters for the system.

        """
        self.components = components
        self.resources = resources

    def get_resource_distribution_dict(self):
        """
        Generate the resource distribution dict based on the specified order.

        The resource distribution dict is formed by grouping resources into four categories:
        1. Bridge Services
        2. Transfer Services
        3. Other Independent Resources
        4. Interdependent Resources

        The reason is that Bridge Services are here assumed always to be independent resources that only affect Transfer Services.
        Transfer Services are assumed to only be affected by Bridge Services and to affect other resources, 
        both the distribution of Independent and Interdependent Resources.
        Remaining Independent Resources can only be distriuted once per time step, as their supply won't be affected by unmet demand for other resources.
        The supply of Interdependent Resources can be affected by unmet demand and to capture potential cascading effects,
        their distribution is last and in an iterative manner.

        TODO: this method can be improved by making it more generic and flexible. Future work.

        Returns:
            dict: A dict separating independent and interdependent resources and specifying the order of resource distribution.

        
        """
        resource_distribution_dict = {'IndependentResources': [],
                                      'InterdependentResources': []}

        # Group resources that belong to the Bridge Services group
        resource_distribution_dict['IndependentResources'] += self.get_resource_group('BridgeService')

        # Group resources that belong to the Transfer Services group
        resource_distribution_dict['IndependentResources'] += self.get_resource_group('TransferService')

        # Separate Independent and Interdependent Resources excluding Bridge and Transfer Services
        resource_distribution_dict = self.get_independent_interdependent_resources(
            resource_distribution_dict)

        # Form the resource distribution vector using Interdependent Resources
        resource_distribution_dict['InterdependentResources'] = self.form_resource_distribution_vector(resource_distribution_dict['InterdependentResources'])

        return resource_distribution_dict

    def get_resource_group(self, group_name: str):
        """
        Get a list of resource names belonging to the specified group.

        Args:
            group_name (str): The name of the resource group.

        Returns:
            list[str]: A list of resource names in the specified group.

        """
        resource_group = []
        for resource_name, resource_parameters in self.resources.items():
            if resource_parameters['Group'] == group_name:
                resource_group.append(resource_name)
        return resource_group

    def get_independent_interdependent_resources(self, resource_distribution_dict: dict):
        """
        Separate resources that are not Bridge or Transfer services into Independent and Interdependent Resources.

        Args:
            resource_distribution_list (list[str]): The list specifying the order of resource distribution.

        Returns:
            tuple[list[str], list[str]]: Two lists containing Independent and Interdependent Resources, respectively.

        """        
        for resource_name in self.resources.keys():
            if resource_name not in resource_distribution_dict['IndependentResources']:
                for component in self.components:
                    if self.resource_is_interdependent(resource_name, component):
                        resource_distribution_dict['InterdependentResources'].append(resource_name)
                        break
                else:
                    resource_distribution_dict['IndependentResources'].append(resource_name)

        return resource_distribution_dict
    
    def resource_is_interdependent(self, resource_name: str, component: Component) -> bool:
        """
        Check whether the specified resource is interdependent.

        A resource is assumed interdependent if there is a single component that:
        1. Has a supply of the resource
        2. Has an operation demand
        3. Component's supply can be affected by unmet demand of the resource (i.e., the relation is not Constant)

        Args:
            resource_name (str): The name of the resource.
            component (Component): The component to check.

        Returns:
            bool: True if the resource is interdependent, False otherwise.

        """
        return component.has_resource_supply(resource_name) and \
               component.has_operation_demand() and \
               component.unmet_demand_can_affect_resource_supply(resource_name)                 

    def form_resource_distribution_vector(self, interdependent_resources):
        """
        Form the resource distribution vector by repeating Interdependent Resources.

        The number of repetitions is equal to the number of Interdependent Resources.

        Reasoning behind this is provided in:
         Blagojevic et al. (2022) Quantifying disaster resilience of a community with
         interdependent civil infrastructure systems

        Args:
            interdependent_resources (list[str]): List of Interdependent Resources.

        Returns:
            list[str]: The resource distribution vector.

        """
        num_resources = len(interdependent_resources)
        return interdependent_resources * num_resources
