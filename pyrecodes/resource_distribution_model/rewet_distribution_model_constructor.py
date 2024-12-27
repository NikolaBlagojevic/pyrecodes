from rewet_API import rewet_pyrecodes_api
from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component

class REWETDistributionModelConstructor(ConcreteResourceDistributionModelConstructor):
    """
    | Class to construct the water distribution model that uses REWET to simulate water flow.
    """

    def construct(self, resource_name: str, resource_parameters: dict, components: list[Component], distribution_model: ResourceDistributionModel):
        super().construct(resource_name, resource_parameters, components, distribution_model)
        r2d_dict = self.create_r2d_dict(components)
        distribution_model.flow_simulator = rewet_pyrecodes_api.REWETPyReCoDes(r2d_dict, 
                                                                               resource_name,
                                                                               resource_parameters['INPFile'],
                                                                               result_dir=resource_parameters['Results_folder'],
                                                                               temp_dir=resource_parameters['Temp_folder'])
        distribution_model.r2d_dict = self.create_r2d_dict(components)

    def create_r2d_dict(self, components):
        """
        | Create a dictionary that follows the structure of the R2D JSON files used to interface with REWET.
        """
        r2d_dict = {}

        for component in components:
            component_type = getattr(component, 'asset_type', None)
            component_subtype = getattr(component, 'asset_subtype', None)
            if component_type is not None and component_type not in r2d_dict.keys():
                r2d_dict[component_type] = {}
            if component_subtype is not None and component_subtype not in r2d_dict[component_type].keys():
                r2d_dict[component_type][component_subtype] = {}
            if hasattr(component, 'r2d_dict_getter'):
                component_r2d_dict = component.r2d_dict_getter.get_dict()
                r2d_dict[component_type][component_subtype][component.aim_id] = component_r2d_dict

        return r2d_dict
