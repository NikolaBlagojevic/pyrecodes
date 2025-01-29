from pyrecodes.resource_distribution_model.abstract_resource_distribution_model import AbstractResourceDistributionModel
from pyrecodes.resource_distribution_model.concrete_resource_distribution_model_constructor import ConcreteResourceDistributionModelConstructor
from pyrecodes.component.component import Component
from pyrecodes.component.standard_irecodes_component import StandardiReCoDeSComponent
from pyrecodes.component.component import SupplyOrDemand
import json
import math

class TransferServiceDistributionModelPotentialPaths(AbstractResourceDistributionModel): 
    """
    | Class to check whether a resource can be transferred between localities. 
    | Potential paths are defined among localities. The class checks whether any of the potential paths can be used to transfer the resource.
    """

    components: list[Component]
    resource_name: str
    potential_paths: dict

    def __init__(self, resource_name: str, resource_parameters: dict, components: list[Component]) -> None:
        self.constructor = ConcreteResourceDistributionModelConstructor()
        self.constructor.construct(resource_name, resource_parameters, components, self)
        self.set_potential_paths(resource_parameters.get("PathSetsFile", ''))
        self.create_potential_paths() 

    def set_potential_paths(self, filename='') -> None:
        if filename == '':
            self.potential_paths_list = dict()
        else:
            with open(filename, 'r') as file:
                self.potential_paths_list = json.load(file)
    
    def create_potential_paths(self) -> None:
        """ 
        | The method finds the links that are used in potential paths. 
        | It creates a list of links that is latter queried to find the 
        optimal path from the list of potential paths.
        """    

        self.potential_paths = {} 
        for path_string, localities_list in self.potential_paths_list.items():       
            self.potential_paths[path_string] = [] 
            start_locality, end_locality = self.get_start_end_locality_from_path_string(path_string)                                  
            for localities in localities_list:
                current_start = start_locality                
                self.initiate_new_link_list(path_string)
                
                for locality in localities[1:]:                
                    self.find_connecting_link(path_string, current_start, locality)

                    if locality == end_locality:                    
                        break
                    else:                    
                        current_start = locality  

    def get_start_end_locality_from_path_string(self, path_string: str) -> tuple:
        return [int(locality) for locality in (path_string.split('from ')[1].split(' to '))]  
    
    def initiate_new_link_list(self, path_string) -> None:
        self.potential_paths[path_string].append([])
    
    def find_connecting_link(self, path_string: str, start_locality: int, next_locality: int):
        for component in self.components:
            if component.locality[0] == start_locality and \
                component.locality[-1] == next_locality and \
                component.has_resource_supply(self.resource_name):
                self.potential_paths[path_string][-1].append(component)
                break

    def distribute(self, time_step: int) -> None:
        """
        | Distribute method updates the potential paths between all locality pairs.
        | This is done implicitly when using the potential path sets,
        as components' transfer service supply is updated in the system class.
        """

        pass                                                                                    
                        
    def get_optimal_path(self, start_locality: int, end_locality: int) -> tuple:
        """
        | Method finds the optimal path, from all potential paths between two localities.
        | Optimality is defined as maximizing the transfer service supply.
        | Transfer service supply of a path is the minimal supply among its constitutive links.
        """   

        potential_path_links = self.potential_paths.get(f'from {int(start_locality)} to {int(end_locality)}', None)
      
        if potential_path_links is None:
            optimal_transfer_supply = 0.0
            optimal_path = None
            return optimal_transfer_supply, optimal_path
        else:
            optimal_path = None
            optimal_transfer_supply = -math.inf
            
            for i, path in enumerate(potential_path_links):        
                path_supply = self.get_path_supply(path)
          
                if path_supply > optimal_transfer_supply:
                    optimal_transfer_supply = path_supply                
                    optimal_path = i
            
            return optimal_transfer_supply, optimal_path      

    def get_path_supply(self, path: list[Component]) -> float:
        """
        Get the supply capacity of a path as the minimum of links supply.
        """    
        
        return min([link.get_current_resource_amount(SupplyOrDemand.SUPPLY.value, 
                                                    StandardiReCoDeSComponent.SupplyTypes.SUPPLY.value, 
                                                    self.resource_name) for link in path])       

    def get_total_supply(self, scope: str) -> float:
        print(f'System supply for transfer service {self.resource_name} not defined yet.')
        return None

    def get_total_demand(self, scope: str) -> float:
        print(f'System demand for transfer service {self.resource_name} not defined yet.')
        return None

    def get_total_consumption(self, scope: str) -> float:
        print(f'System consumption for transfer service {self.resource_name} not defined yet.')   
        return None

