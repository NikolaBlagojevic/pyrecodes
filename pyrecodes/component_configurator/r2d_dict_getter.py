from pyrecodes.component.component import Component

class R2DDictGetter():
    """
    Class used to create a dictionary representing component characteristics to recreate the R2D JSON file later used to call resource distribution models.

    Component characteristics are obtained from the component object.
    """

    def __init__(self, component: Component) -> None:
        self.component = component

    def get_dict(self) -> dict:
        return {'GeneralInformation': self.component.general_information,
                'Damage': {}}
    
class R2DPipeDictGetter(R2DDictGetter):

    def get_dict(self) -> dict:
        return {'GeneralInformation': self.component.general_information,
                'Damage': self.component.damage_information}
                  
