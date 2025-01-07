from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.probability_distribution import probability_distribution
import numpy as np

class InfrastructureInterface(StandardiReCoDeSComponent):
    """
    | Subclass of the StandardiReCoDeSComponent class used to interface the outputs of third-party infrastructure simulators into an iRe-CoDeS system-of-systems model.
    | Infrastructure simulator performance is defined in the system configuration file. 
    | This interface implements the Tier 1 and Tier 2 infrastructure interfaces as defined in https://doi.org/10.1007/s10669-023-09931-0.
    """   
    def set_supply_dynamics(self, supply_dynamics: dict) -> None:   
        """
        | Set the predefined supply dynamics of the infrastructure interface component by specifying the parameters of the component's recovery model.
        | These are defined in the system configuration file by specifying the amounts of resource supplied by the infrastructure system and the time step at which the supply is restored.
        | **Note 1**: The supply dynamics are defined in the system configuration file, but in the component library file the interface component has to have the resource defined.
        | **Note 2**: It is assumed that last value in the Amount key is the initial supply amount and the highest value that the infrastructure system provides. 
        """
        restoration_times = self.get_restoration_times(supply_dynamics)
        total_restoration_time = max(restoration_times)
        # avoid divison with zero if the last restoration time is zero
        if restoration_times[-1] != 0.0:
            step_limits = list(np.divide(restoration_times, total_restoration_time))
        else:
            step_limits = [1.0]
        step_values = list(np.divide(supply_dynamics['Amount'], max(supply_dynamics['Amount'])))   
        step_limits, step_values = self.add_initial_zero_supply(step_limits, step_values)
        
        self.recovery_model.set_parameters({'RestoredIn': total_restoration_time,
                                            'StepLimits': step_limits,
                                            'StepValues': step_values})
        self.supply['Supply'][supply_dynamics['Resource']].set_initial_amount(max(supply_dynamics['Amount']))
    
    def add_initial_zero_supply(self, step_limits: list, step_values: list) -> tuple:
        """
        | Add the initial zero supply to the step limits and step values.
        | This is needed to make sure that the supply is zero before the infrastructure system is restored.
        | This is not applied if the interface already defines the initial post-disaster supply amount at time 0.
        """
        if step_limits[0] != 0.0:
            step_limits.insert(0, 0.0)
            step_values.insert(0, 0.0)
        return step_limits, step_values
    
    def get_restoration_times(self, supply_dynamics: dict) -> list:
        """
        | Sample the restoration times from the distribution defined in the system configuration file.
        | These times define the time steps at which the interface restors the supply amounts defined in the Amount key in the system configuration file.
        """
        restoration_times = []
        for restoration_time_dict in supply_dynamics.get('RestoredIn', []):
            distribution_name, distribution_parameters = list(restoration_time_dict.items())[0]
            restoration_time = getattr(probability_distribution, distribution_name)(distribution_parameters).sample()
            restoration_times.append(restoration_time)
        return restoration_times

