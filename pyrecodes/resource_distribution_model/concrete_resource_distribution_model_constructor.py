from pyrecodes.resource_distribution_model.resource_distribution_model_constructor import ResourceDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component

class ConcreteResourceDistributionModelConstructor(ResourceDistributionModelConstructor):
    """
    Class for constructing resource distribution models.
    """

    def construct(self, resource_name: str, resource_parameters: dict, components: list[Component], distribution_model: ResourceDistributionModel):
        self.set_resource_name(resource_name, distribution_model)
        self.set_components(components, distribution_model)
        self.set_time_stepping_rules(resource_parameters.get('DistributionTimeStepping', []), distribution_model)
    
    def set_resource_name(self, resource_name: str, distribution_model: ResourceDistributionModel) -> None:
        distribution_model.resource_name = resource_name

    def set_components(self, components: list[Component], distribution_model: ResourceDistributionModel) -> None:
        distribution_model.components = components    

    def set_time_stepping_rules(self, time_stepping_rules: list, distribution_model: ResourceDistributionModel) -> None:
        distribution_time_steps = []
        for time_stepping in time_stepping_rules:
            distribution_time_steps += list(range(time_stepping['start'], time_stepping['end'], time_stepping['step']))
        distribution_model.set_distribution_time_steps(distribution_time_steps) 