from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component
from pyrecodes.utilities import get_class
from pyrecodes.resource_distribution_model.single_resource_system_matrix_creator import SingleResourceSystemMatrixCreator

class UtilityDistributionModelConstructor(ConcreteResourceDistributionModelConstructor):
    """
    Class for constructing the Utility Distribution Model.
    """

    def construct(self, resource_name: str, resource_parameters: dict, components: list[Component], distribution_model: ResourceDistributionModel):
        super().construct(resource_name, resource_parameters, components, distribution_model)
        self.set_priority_model(resource_name, resource_parameters['DistributionPriority'], components, distribution_model)
        self.set_system_matrix(components, resource_name, distribution_model)
    
    def set_priority_model(self, resource_name: str, distribution_priority: dict, components: list[Component], distribution_model: ResourceDistributionModel) -> None:
        target_priority_model = get_class(distribution_priority['FileName'], distribution_priority['ClassName'], 'distribution_priority')
        priority_model = target_priority_model(resource_name, distribution_priority['Parameters'], components)
        distribution_model.priority = priority_model
    
    def set_system_matrix(self, components: list[Component], resource_name: str, distribution_model: ResourceDistributionModel) -> None:
        distribution_model.system_matrix = SingleResourceSystemMatrixCreator(components, resource_name)
    
    def set_transfer_service_distribution_model(self, transfer_service_distribution_model: ResourceDistributionModel, distribution_model: ResourceDistributionModel) -> None:
        """
        **TODO**: Implement this method to consider the transfer service distribution model.
        """
        self.transfer_service_distribution_model = None 