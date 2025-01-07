from rewet_API import rewet_pyrecodes_api
from pyrecodes.resource_distribution_model.simcenter_resource_distribution_model_constructor import SimCenterResourceDistributionModelConstructor
from pyrecodes.resource_distribution_model.resource_distribution_model import ResourceDistributionModel
from pyrecodes.component.component import Component

class REWETDistributionModelConstructor(SimCenterResourceDistributionModelConstructor):

    def construct(self, resource_name: str, resource_parameters: dict, components: list[Component], distribution_model: ResourceDistributionModel):
        super().construct(resource_name, resource_parameters, components, distribution_model)
        distribution_model.flow_simulator = rewet_pyrecodes_api.REWETPyReCoDes(self.r2d_dict, 
                                                                               resource_name,
                                                                               resource_parameters['INPFile'],
                                                                               result_dir=resource_parameters['Results_folder'],
                                                                               temp_dir=resource_parameters['Temp_folder'])
        distribution_model.r2d_dict = self.create_r2d_dict(components)
