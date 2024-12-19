from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component

class ResidualDemandTrafficDistributionModelConstructor(ConcreteResourceDistributionModelConstructor):

    # from residual_demand_traffic_simulator import residual_demand_assignment

    def construct(self, resource_name: str, resource_parameters: dict, components: list([Component]), distribution_model: ResourceDistributionModel):
        super().construct(resource_name, resource_parameters, components, distribution_model)
        # distribution_model.traffic_simulator = self.residual_demand_assignment.main
        distribution_model.traffic_simulator = None
        distribution_model.r2d_dict = self.create_r2d_dict(components)
        distribution_model.od_matrix = self.create_od_matrix(components)

    def create_r2d_dict(self, components):
        """
        Create a dictionary that follows the structure of the R2D JSON files used as inputs for the residual demand traffic simulator.
        
        The dictionary consists of component characteristics of the transportation network.
        """

        r2d_dict = {"TransportationNetwork": {"Bridge": {}, "Tunnel": {}, "Roadway": {}}}

        for component in components:
            component_type = getattr(component, 'asset_subtype', None)
            if component_type in r2d_dict["TransportationNetwork"].keys():
                component_r2d_dict = component.r2d_dict_getter.get_dict()
                r2d_dict["TransportationNetwork"][component_type][component.aim_id] = component_r2d_dict
        
        return r2d_dict
    
    def create_od_matrix(self, components):
        # TODO: Implement method to create OD matrix from components. If we can create an OD matrix based on the R2D JSON file then this method is not needed.
        return []
