from abc import ABC, abstractmethod

class RecoveryActivity(ABC):
    """
    Abstract class representing a recovery activity.

    Attributes:
        level (float): The current progress level of the activity at a time step (between 0 and 1).
        duration (float): The duration of the activity.
        rate (float): The rate of progress per time unit.
        preceding_activities (list[str]): List of names of preceding activities that have to be completed until this activity can start.
        preceding_activities_finished (bool): True if all preceding activities are finished.
        demand_met (float): The percent of demand met.
        name (str): The name of the recovery activity.
        time_steps (list[int]): List of time steps when progress was recorded.
    """
    level: float
    duration: float
    rate: float
    preceding_activities: list([str])
    preceding_activities_finished: bool
    demand_met: float
    name: str
    time_steps: list([int])

    @abstractmethod
    def __init__(self, name: str) -> None:
        pass

    @abstractmethod
    def set_name(self, name: str) -> None:
        pass

    @abstractmethod
    def set_level(self, level: float) -> None:
        pass

    @abstractmethod
    def set_duration(self, distribution: dict) -> None:
        pass

    @abstractmethod
    def sample_duration(self, distribution: dict) -> float:
        pass

    @abstractmethod
    def set_preceding_activities(self, preceding_activities: list([str])) -> None:
        pass    

    @abstractmethod
    def set_preceding_activities_finished(self, finished: bool) -> None:
        pass

    @abstractmethod
    def set_demand(self, resources: list) -> None:
        pass

    @abstractmethod
    def set_demand_met(self) -> None:
        pass

    @abstractmethod
    def get_demand(self) -> dict:
        pass

    @abstractmethod
    def recover(self, time_step: int) -> None:
        pass

    @abstractmethod
    def record_progress(self, time_step: int) -> None:
        pass

    @abstractmethod
    def activity_finished(self) -> bool:
        pass
