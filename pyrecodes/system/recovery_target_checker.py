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
