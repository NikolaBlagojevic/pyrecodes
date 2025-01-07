from pyrecodes.resource_distribution_model.simcenter_resource_distribution_model_constructor import SimCenterResourceDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component
from residual_demand_API import transportation


class ResidualDemandTrafficDistributionModelConstructor(SimCenterResourceDistributionModelConstructor):

    def construct(self, resource_name: str, resource_parameters: dict, components: list[Component], distribution_model: ResourceDistributionModel):
        super().construct(resource_name, resource_parameters, components, distribution_model)
        distribution_model.TRIP_CUTOFF_THRESHOLD = resource_parameters['TripCutoffThreshold']
        distribution_model.flow_simulator = transportation.pyrecodes_residual_demand(
            resource_parameters['EdgeFile'], resource_parameters['NodeFile'],
            resource_parameters['ODFilePre'], resource_parameters['HourList'], 
            resource_parameters['ResultsFolder'],
            resource_parameters['CapacityRuleset'], resource_parameters['DemandRuleset'],
            resource_parameters['TwoWayEdges']
        )
        distribution_model.r2d_dict = self.r2d_dict
