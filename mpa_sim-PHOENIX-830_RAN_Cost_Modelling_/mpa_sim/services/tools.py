import os
from types import SimpleNamespace
import numpy as np
import pandas as pd
import math


import mpa_sim

np.random.seed(42)


class Calculator(object):
    """

    A model to calculate the theoritical figures.

    Parameters
    ----------
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """

    def __init__(self, simulation_parameters) -> None:

        self.params = simulation_parameters
        
        # a dict with tuple key as (freq, numerology) and value of Max Transmission Bandwidth
        self.nbr = {(5,0):25, (10,0):52, (15,0):79, (20,0):106, (25,0):133, (30,0):160, (40,0):216, (50,0):270,
        (5,1):11, (10,1):24, (15,1):38, (20,1):51, (25,1):65, (30,1):78, (40,1):106, (50,1):133, (60,1):162, 
        (70,1):189, (80,1):217, (90,1):245, (100,1):273, (10,2):11, (15,2):18, (20,2):24,(25,2):31, (30,2):38, 
        (40,2):51, (50,2):65, (60,2):79, (70,2):93, (80,2):107, (90,2):121, (100,2):135}


    def max_cell_throughput(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the maximum throughput of 5G NR network for user (depending on his mobile device UE).
        Approximately data transfer rate of 5G NR can be calculated using the formula based on the 3GPP TS 38.306 standard.

        Parameters
        ----------
            mode : string 
                Modulation mode [FDD (frequency division duplex) | TDD (time division duplex)].


        Returns
        -------
            throughput : dict
                a dictionary contains DL and UL throughput in Gbps {UL: float Gbps, DL: float Gbps}
                


        """

        # ref: Energy Efficiency Gains in Interference-limitedHeterogeneous Cellular Mobile Radio Networkswith Random Micro Site Deployment
        # https://www.researchgate.net/publication/224242017_Energy_efficiency_gains_in_interference-limited_heterogeneous_cellular_mobile_radio_networks_with_random_micro_site_deployment

        modulation_order = math.log2(self.params['Modulation'])

        ts = (10**-3) / (14 * 2**self.params['Numerology'])


        dl = 10**-6 \
            * self.params['number_of_aggregated_component_carriers'] \
            * self.params['DL_MIMO_Layers'] \
            * self.params['MU_MIMO'] \
            * modulation_order \
            * self.params['Rmax'] \
            * self.params['Scaling_factor'] \
            * self.nbr[(self.params['Bandwidth'], self.params['Numerology'])] \
            * 12 \
            * (1 - self.params['signaling_overhead']) \
            / ts


        ul = 10**-6 \
            * self.params['number_of_aggregated_component_carriers'] \
            * self.params['UL_MIMO_Layers'] \
            * self.params['MU_MIMO'] \
            * modulation_order \
            * self.params['Rmax'] \
            * self.params['Scaling_factor'] \
            * self.nbr[(self.params['Bandwidth'], self.params['Numerology'])] \
            * 12 \
            * (1 - self.params['signaling_overhead']/1.75) \
            / ts

        if mode == 'TDD':
            dl *= self.params['DL_UP_ratio'] 
            ul *= (1 - self.params['DL_UP_ratio'])
               
        return {'DL': dl/1000, 'UL': ul/1000}


    def ecpri_throughput(self) -> float:
        """

        Сalculator to calculate the FH throughput(eCPRI) of 5G NR network for user (depending on his mobile device UE).
        considering the IQ compression and signalling overhead

        Parameters
        ----------
            mode : string 
                Modulation mode [FDD (frequency division duplex) | TDD (time division duplex)].


        Returns
        -------
            throughput : float
                throughput requires to be maintain at eCPRI

        """

        # symbole duration 
        Symbol_duration = (10**-3) / (2**self.params['Numerology'])

        symbols_in_slot = 14 # Maximum number of symbols in slot 5g
        num_subcarrier_per_RB = 12 # a resource block (RB) in NR is defined as 12 consecutive subcarriers

        datarate = self.params['Number_of_logical_antenna_ports'] \
            * symbols_in_slot \
            / Symbol_duration \
            * self.nbr[(self.params['Bandwidth'], self.params['Numerology'])] \
            * num_subcarrier_per_RB \
            * (self.params['IQ_mantissa_bitwidth'] * 2 + self.params['IQ_exp_bitwidth']) \
            / 10**9

        throughput = datarate * (1+ self.params['signaling_overhead'])

        return throughput
        
    def f1c_throughput(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1c of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1c

        """

        # symbole duration 
        ecpri_tput = max(self.max_cell_throughput(mode).values())
        return ecpri_tput * self.params['signaling_overhead'] * self.params['ru_du_ratio']


    def f1u_throughput(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1u of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1u

        """

        # symbole duration 
        ecpri_tput = max(self.max_cell_throughput(mode).values())
        return ecpri_tput * (1-self.params['signaling_overhead']) * self.params['ru_du_ratio']


    def du_nb_traffic(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1u of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1u

        """

        # symbole duration 
        
        return self.f1c_throughput(mode) + self.f1u_throughput(mode)

    def cuup_nb_traffic(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1u of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1u

        """

        # symbole duration 
        
        return self.f1u_throughput(mode) * self.params['du_cuup_ratio']

    def cucp_nb_traffic(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1u of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1u

        """

        # symbole duration 
        
        return self.f1c_throughput(mode) * self.params['du_cuup_ratio'] * self.params['cucp_cuup_ratio']

    def core_traffic(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1u of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1u

        """

        # symbole duration 
        
        return self.cuup_nb_traffic(mode) * self.params['cucp_cuup_ratio']

    def smo_traffic(self, mode = 'TDD') -> float:
        """

        Сalculator to calculate the max f1u of 5G NR network for user.

        Parameters
        ----------


        Returns
        -------
            throughput : float
                throughput requires to be maintain at f1u

        """

        # symbole duration 
        
        return self.cucp_nb_traffic(mode)

 