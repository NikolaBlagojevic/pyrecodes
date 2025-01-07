from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor

class SimCenterResourceDistributionModelConstructor(ConcreteResourceDistributionModelConstructor):
     
    def construct(self, resource_name, resource_parameters, components, distribution_model):
        super().construct(resource_name, resource_parameters, components, distribution_model)
        self.create_r2d_dict(components)

    def create_r2d_dict(self, components):
        """
        Create a dictionary that follows the structure of the R2D JSON files used as inputs for the resource distribution simulators implemented by the SimCenter.

        """
        self.r2d_dict = {}

        for component in components:
            component_type = getattr(component, 'asset_type', None)
            component_subtype = getattr(component, 'asset_subtype', None)
            if component_type is not None and component_type not in self.r2d_dict.keys():
                self.r2d_dict[component_type] = {}
            if component_subtype is not None and component_subtype not in self.r2d_dict[component_type].keys():
                self.r2d_dict[component_type][component_subtype] = {}
            if hasattr(component, 'r2d_dict_getter'):
                component_r2d_dict = component.r2d_dict_getter.get_dict()
                self.r2d_dict[component_type][component_subtype][component.aim_id] = component_r2d_dict
        return self.r2d_dict

        

