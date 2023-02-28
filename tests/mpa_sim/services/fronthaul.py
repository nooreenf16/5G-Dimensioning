import numpy as np
import sys

from mpa_sim.services.path_loss import path_loss_calculator

np.random.seed(42)

class fronthaul_sim(object):
    """

    Meta-object for managing all fronthual related communications.

    Parameters
    ----------
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """
    def __init__(self, simulation_parameters):

        self.simulation_parameters = simulation_parameters

    def estimate_fronthaul_capacity(self, capacity, modulation):
        """
        Uses the modulation and the estimated capacity to identify the capacity on the fronthaul link.

        Parameters
        ----------
        capacity : float
            capacity can be delivered on the air-interface in Mbps.
        generation : string
            Either 4G or 5G dependent on technology.
        modulation : string
            Type of mudulation being used.


        Returns
        -------
        estimate_fronthaul_capacity : float
            estimated capacity on the fronthaul link in Mpbs.

        """
        
        if self.simulation_parameters['modulation_compression'] and capacity > 0 and modulation is not None:
            return capacity * self.simulation_parameters['compression_ratio'][modulation]

        return capacity
