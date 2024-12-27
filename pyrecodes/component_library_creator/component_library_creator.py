"""
Module used to create component library based on which system components are constructed.
"""

from abc import ABC, abstractmethod

class ComponentLibraryCreator(ABC):
    """
    Interface for ComponentLibraryCreator class used to create component library based on which system components are constructed.
    """

    library: dict

    @abstractmethod
    def form_library(self) -> dict:
        pass
