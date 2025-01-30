from abc import ABC, abstractmethod
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component

class ResourceDistributionModelConstructor(ABC):
    """
    Inteface for the class constructing resource distribution models.
    """

    @abstractmethod
    def set_components(self, components: list[Component], distribution_model: ResourceDistributionModel) -> None:
        pass

    @abstractmethod
    def set_resource_name(self, resource_name: str) -> None:
        pass