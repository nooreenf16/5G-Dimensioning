import os
import numpy as np
import pandas as pd
import math


from mpa_sim.services.tools import Calculator
from mpa_sim.services.overhead_calulation import overhead_per_server

np.random.seed(42)


class Cost(object):
    """

    A model to estimate the cost.

    Parameters
    ----------
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    cost_parameters : dict
        A dict containing all cost parameters.

    """

    def __init__(self, simulation_parameters, cost_parameters) -> None:

        self.simulation_parameters = simulation_parameters
        self.cost_parameters = cost_parameters
        self.calculator = Calculator(simulation_parameters = simulation_parameters)

    def get_sites_per_km2(self, site_radius) -> float:
        """

        A forcasting model to predict the utilizadtion of CPU for CU and DU based on Radisys test results.

        Parameters
        ----------
        site_radius : int
            Radius of site area in meters.

        sites_per_km2 : float
            number of sites per km2.

        """

        #ref: Energy Efficiency Gains in Interference-limitedHeterogeneous Cellular Mobile Radio Networkswith Random Micro Site Deployment
        # https://www.researchgate.net/publication/224242017_Energy_efficiency_gains_in_interference-limited_heterogeneous_cellular_mobile_radio_networks_with_random_micro_site_deployment

        inter_site_distance = site_radius * 2
        site_area_km2 = (math.sqrt(3) / 2) * inter_site_distance ** 2 / 1e6
        sites_per_km2 = 1 / site_area_km2
        return sites_per_km2

    def discount_ownership_cost(self, cost, capex) -> float:
        """
        Discount costs based on asset_lifetime.

        Parameters
        ----------
        capex : boolean
            specifies if the cost is a capex (True) or opex (False)

        Returns
        -------
            total_cost_of_ownership : float
                total cost of the ownership over the asset lifetime considering the discount 
                
        """
        asset_lifetime = self.simulation_parameters['asset_lifetime']
        discount_rate = self.simulation_parameters['discount_rate'] / 100

        if capex:
            capex = cost

            opex = round(capex * (self.simulation_parameters['opex_percentage_of_capex'] / 100))

            total_cost_of_ownership = 0
            total_cost_of_ownership += capex

            for i in range(0, asset_lifetime ):
                total_cost_of_ownership += (
                    opex / (1 + discount_rate) ** i
                )
        else:
            opex = cost
            total_cost_of_ownership = 0

            for i in range(0, asset_lifetime ):
                total_cost_of_ownership += (
                    opex / (1 + discount_rate) ** i
                )

        return total_cost_of_ownership

    def cost_optimized(self, component, **kwargs):
        selected_idx = -1
        for idx , val in enumerate(self.cost_parameters[component]):
            selected = True
            for key, value in kwargs.items():
                if self.cost_parameters[component][idx][key] < value:
                    selected = False
                    break
            if selected:
                if selected_idx == -1: 
                    selected_idx = idx
                else: 
                    if self.cost_parameters[component][idx]['price'] < self.cost_parameters[component][selected_idx]['price']:
                        selected_idx = idx

        return self.cost_parameters[component][selected_idx]

    def serv_cost(self, cpu_util, max_utilization = 80):
        """

        Radio site contains RU and Antenas
        No sharing takes place.

        Parameters
        ----------
        cpu_util : flaot percentages
            a float number showing the percenatges of overal CPU Cores for CU for a sector.

        max_utilization:
            Each core utilizes a max of 80% of its capabilites

        Returns
        -------
        server cost breakdown : dict
            cost breakdown for the radio site { "cpu_price": cost in USD, 
                                                "server_price": cost in USD, 
                                                "number_of_servers": number of required servers   }

        
        To be added
        -----------
        consideing more veriety of servers and cpus
        considering max number of PCIe cards required for L1 

        """

        #combining overhead calculation with cost calculation
        max_utilization = max_utilization - overhead_per_server(self.simulation_parameters['type_of_server'],self.simulation_parameters['type_of_virtualization'],self.simulation_parameters['prop_or_not'],self.simulation_parameters['n_virtual_machines'])

        number_of_cores = cpu_util / max_utilization
        number_of_cpus = number_of_cores / self.cost_parameters['cpu'][0]['cores']
        cpu_price = number_of_cpus * self.cost_parameters['cpu'][0]['price']

        number_of_servers = number_of_cpus / self.cost_parameters['server'][0]['cpu_max']
        server_price = number_of_servers * self.cost_parameters['server'][0]['price']

        return {"cpu_price": cpu_price, 
                "server_price": server_price, 
                "number_of_cpus": number_of_cpus,
                "number_of_servers": number_of_servers}

    def get_cost(self, sites_per_km2, capacity_gbps, rudu_distance, ducu_distance, CUCP_utils, CUUP_utils, DU_utils):
        """

        Radio site contains RU and Antenas
        No sharing takes place.

        Parameters
        ----------
        sites_per_km2 : float
            number of sites per km2.

        capacity_gbps : float
            required capacity to serve UEs in a sector in Gbps; the value per site is capacity_gbps x count_of_sectors
        
        rudu_distance: float
            distance between RU and DU in meters

        ducu_distance: float
            distance between DU and CU_CP in meters; CU_UP can be either collocated with CU_CP or DU

        CU_utils : flaot percentages
            a float number showing the percenatges of overal CPU Cores for CU for a sector.

        CUCP_utils : flaot percentages
            a float number showing the percenatges of overal CPU Cores for CU_CP for a sector.

        CUUP_utils : flaot percentages
            a float number showing the percenatges of overal CPU Cores for CU_UP for a sector.

        DU_utils : flaot percentages
            a float number showing the percenatges of overal CPU Cores for DU for a sector.

        Returns
        -------
        {cost_breakdown, components_breakdown} : dict of dict
            cost cost_breakdown and  components_breakdown for the radio site { "item": cost in USD  }
            components_breakdown is based on one complete branch of connection consisting of ru_du_ratio * du_cuup_ratio

        """

        sites_per_du = sites_per_km2 * self.simulation_parameters['sectorization'] / self.simulation_parameters['ru_du_ratio']
        FH_tput = self.calculator.ecpri_throughput()
        
        cost_breakdown = {
            'single_sector_antenna': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'single_sector_antenna'
                    )['price'], 1) * 
                    self.simulation_parameters['sectorization'] *
                    sites_per_km2
            ),
            'ru': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'ru'
                    )['price'], 1) * 
                    self.simulation_parameters['sectorization'] *
                    sites_per_km2
            ),
            'tower': (
                self.cost_optimized(
                    'tower'
                )['price'] *
                sites_per_km2
            ),  
            'transportation': (
                self.cost_optimized(
                    'transportation'
                )['price'] *
                sites_per_km2
            ),          
            'installation': (
                self.cost_optimized(
                    'installation'
                )['price'] *
                sites_per_km2
            ),
            'site_rental': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'site_rental'
                    )['price'], 0) *
                sites_per_km2
            ),
            'power_generator_battery_system': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'power_generator_battery_system'
                    )['price'], 1) *
                sites_per_km2
            ),
            'fiber_switch': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'switch',
                        ports = self.simulation_parameters['sectorization'] + 1,
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                    )['price'], 1) *
                sites_per_km2
            ),
            'sfp_ru': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'sfp',
                        distance = rudu_distance, #15Km
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                    )['price'], 1) * 2 * # one on the ru side and one in du
                sites_per_km2
            ),
            'sfp_sectors': (
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'sfp',
                        distance = 100, #meters
                        speed = capacity_gbps
                    )['price'], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2
            ),
            'eCPRI_leased_line_capex': (
                self.discount_ownership_cost( # Cost of initial installationthe fixed part ru-du
                    self.cost_optimized(
                        'lease_line_installation',
                        speed = FH_tput * self.simulation_parameters['sectorization']
                    )['price'] +  
                    self.cost_optimized( # Cost of initial installationthe variable part by meter distance ru-du
                        'lease_line_installation_per_meter',
                        speed = FH_tput * self.simulation_parameters['sectorization']
                    )['price'] * rudu_distance
                    , 1) * 
                sites_per_km2
            ),
            'eCPRI_leased_line_opex': (  # Rental cost for the ru-du leased line
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'lease_line_rental',
                        speed = FH_tput * self.simulation_parameters['sectorization']
                    )['price'], 0) *
                sites_per_km2
            ),
            'f1u_leased_line_capex': (
                self.discount_ownership_cost( # Cost of initial installationthe fixed part cu_up-du 
                    self.cost_optimized(
                        'lease_line_installation',
                        speed = capacity_gbps * self.simulation_parameters['sectorization'] 
                                * self.simulation_parameters['ru_du_ratio']
                                * (1 - self.simulation_parameters['signaling_overhead'])
                    )['price'] +  
                    self.cost_optimized( # Cost of initial installationthe variable part by meter distance cu_up-du
                        'lease_line_installation_per_meter',
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                                * self.simulation_parameters['ru_du_ratio']
                                * (1 - self.simulation_parameters['signaling_overhead'])
                    )['price'] * ducu_distance
                    , 1) * 
                sites_per_du
            ),
            'f1u_leased_line_opex': (  # Rental cost for the cu_up-du leased line
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'lease_line_rental',
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                                * self.simulation_parameters['ru_du_ratio']
                                * (1 - self.simulation_parameters['signaling_overhead'])
                    )['price'], 0) *
                sites_per_du
            ),
            'f1c_leased_line_capex': (
                self.discount_ownership_cost( # Cost of initial installationthe fixed part cu_cp-du
                    self.cost_optimized(
                        'lease_line_installation',
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                                * self.simulation_parameters['ru_du_ratio']
                                * self.simulation_parameters['signaling_overhead']
                    )['price'] +  
                    self.cost_optimized( # Cost of initial installationthe variable part by meter distance cu_cp-du
                        'lease_line_installation_per_meter',
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                                * self.simulation_parameters['ru_du_ratio']
                                * self.simulation_parameters['signaling_overhead']
                    )['price'] * ducu_distance
                    , 1) * 
                sites_per_du
            ),
            'f1c_leased_line_opex': (  # Rental cost for the cu_cp-du leased line
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'lease_line_rental',
                        speed = capacity_gbps * self.simulation_parameters['sectorization']
                                * self.simulation_parameters['ru_du_ratio']
                                * self.simulation_parameters['signaling_overhead']
                    )['price'], 0) *
                sites_per_du
            ),
            'l1_controller': (  # cost for the L1 PCIe card Controller 
                self.discount_ownership_cost(
                    self.cost_optimized(
                        'l1_controller' 
                    )['price'], 1) *
                sites_per_km2 / 
                self.cost_optimized('l1_controller' )['ports']
            ),
            'cucp_cpu': ( #cost for the CU-CP CPU per km2
                self.discount_ownership_cost(
                    self.serv_cost(CUCP_utils)["cpu_price"], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2 
            ),
            'cucp_server': ( #cost for the CU-CP CPU per km2
                self.discount_ownership_cost(
                    self.serv_cost(CUCP_utils)["server_price"], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2 
            ),
            'cuup_cpu': ( #cost for the CU-UP CPU per km2
                self.discount_ownership_cost(
                    self.serv_cost(CUUP_utils)["cpu_price"], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2 
            ),
            'cuup_server': ( #cost for the CU-UP CPU per km2
                self.discount_ownership_cost(
                    self.serv_cost(CUUP_utils)["server_price"], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2 
            ),
            'du_cpu': ( #cost for the DU CPU per km2
                self.discount_ownership_cost(
                    self.serv_cost(DU_utils)["cpu_price"], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2 
            ),
            'du_server': ( #cost for the DU CPU per km2
                self.discount_ownership_cost(
                    self.serv_cost(DU_utils)["server_price"], 1) *
                self.simulation_parameters['sectorization'] *
                sites_per_km2 
            ),

        }

        site_count = self.simulation_parameters['ru_du_ratio'] * self.simulation_parameters['du_cuup_ratio']/self.simulation_parameters['sectorization']

        components_breakdown = {
            'single_sector_antenna': site_count * self.simulation_parameters['sectorization'],
            'ru': site_count * self.simulation_parameters['sectorization'],
            'tower': site_count,  
            'power_generator_battery_system': site_count,
            'fiber_switch': site_count,
            'sfp': site_count * self.simulation_parameters['sectorization'] * 2,
            'eCPRI_Throughput(Gbps)': FH_tput * self.simulation_parameters['sectorization'],
            'f1u_Throughput(Gbps)': capacity_gbps * self.simulation_parameters['sectorization'] 
                                * self.simulation_parameters['ru_du_ratio']
                                * (1 - self.simulation_parameters['signaling_overhead']),
            'f1c_Throughput(Gbps)': capacity_gbps * self.simulation_parameters['sectorization']
                                * self.simulation_parameters['ru_du_ratio']
                                * self.simulation_parameters['signaling_overhead'],
            'l1_controller': site_count * self.simulation_parameters['sectorization']/4,
            'cucp_cpu': self.serv_cost(CUCP_utils)["number_of_cpus"] 
                        * self.simulation_parameters['sectorization'] 
                        * site_count,
            'cucp_server': self.serv_cost(CUCP_utils)["number_of_servers"]
                * self.simulation_parameters['sectorization']
                * site_count, 
            'cuup_cpu': self.serv_cost(CUUP_utils)["number_of_cpus"] 
                        * self.simulation_parameters['sectorization'] 
                        * site_count,
            'cuup_server': self.serv_cost(CUUP_utils)["number_of_servers"]
                * self.simulation_parameters['sectorization']
                * site_count, 
            'du_cpu': self.serv_cost(DU_utils)["number_of_cpus"] 
                        * self.simulation_parameters['sectorization'] 
                        * site_count,
            'du_server': self.serv_cost(DU_utils)["number_of_servers"]
                * self.simulation_parameters['sectorization']
                * site_count, 
        }


        return {"cost_breakdown": cost_breakdown, "components_breakdown": components_breakdown}





