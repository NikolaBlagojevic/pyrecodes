from abc import ABC, abstractmethod
import math
from pyrecodes.system.system import System

class RecoveryTargetChecker(ABC):
    """
    Abstract base class for a recovery target checker.

    This class defines the interface for checking whether the system has recovered and the resilience assessment interval
    is finished.
    """

    @abstractmethod
    def recovery_target_met(self, system: System) -> bool:
        """
        Check whether the recovery target has been met for the given system.

        Args:
            system (System): The system object to check for recovery.

        Returns:
            bool: True if the recovery target is met, False otherwise.
        """
        pass


class NoDamageRecoveryTargetChecker(RecoveryTargetChecker):
    """
    Concrete subclass of RecoveryTargetChecker.

    This class implements the recovery target checker where the system has recovered once all components are damage-free.

    """

    def recovery_target_met(self, system: System) -> bool:
        """
        Check whether the recovery target has been met for the given system.

        The system is considered to have recovered once all components are damage-free (damage level close to 0).

        Args:
            system (System): The system object to check for recovery.

        Returns:
            bool: True if the recovery target is met, False otherwise.
        """
        if system.time_step <= system.DISASTER_TIME_STEP:
            return False
        else:
            for component in system.components:
                if not (math.isclose(component.get_damage_level(), 0, abs_tol=1e-10)):
                    return False
        return True


class NoDamageRecoveryTargetWithExtraTimeChecker(RecoveryTargetChecker):
    """
    Subclass of RecoveryTargetChecker.

    This class implements the recovery target checker where the system has recovered once all components are damage-free and then simulates an extra time step to ensure the system is stable.

    """
    def __init__(self):
        self.damage_free_time_step = None

    def recovery_target_met(self, system: System, extra_time_steps=10) -> bool:
        """
        Check whether the recovery target has been met for the given system.

        The system is considered to have recovered once all components are damage-free (damage level close to 0) and then simulates an extra time step.

        Args:
            system (System): The system object to check for recovery.

        Returns:
            bool: True if the recovery target is met, False otherwise.
        """
        if system.time_step <= system.DISASTER_TIME_STEP:
            return False
        else:
            for component in system.components:
                if not (math.isclose(component.get_damage_level(), 0, abs_tol=1e-10)):
                    return False
            else:
                if self.damage_free_time_step is None:
                    self.damage_free_time_step = system.time_step

        if self.damage_free_time_step is not None and system.time_step >= self.damage_free_time_step + extra_time_steps:
            return True
        else:
            return False
