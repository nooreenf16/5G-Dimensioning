import sys
import pytest

from mpa_sim.services.costs import Cost

PARAMETERS = {
    'iterations': 20,
    'seed_value1': 1,
    'seed_value2': 2,
    'indoor_users_percentage': 50,
    'los_breakpoint_m': 500,
    'tx_macro_baseline_height': 30,
    'tx_macro_power': 40,
    'tx_macro_gain': 16,
    'tx_macro_losses': 1,
    'tx_micro_baseline_height': 10,
    'tx_micro_power': 24,
    'tx_micro_gain': 5,
    'tx_micro_losses': 1,
    'rx_gain': 4,
    'rx_losses': 4,
    'rx_misc_losses': 4,
    'rx_height': 1.5,
    'building_height': 5,
    'street_width': 20,
    'above_roof': 0,
    'network_load': 50,
    'percentile': 50,
    'sectorization': 3,
    'mnos': 2,
    'asset_lifetime': 10,
    'discount_rate': 3.5,
    'opex_percentage_of_capex': 10,
    'signaling_overhead': 0.18, # overhead for control channels
    'modulation_compression': True,
    'ru_du_ratio': 10,
    'du_cu_ratio': 1,
    'compression_ratio': {
        'QPSK': 0.06,
        '16QAM': 0.12,
        '64QAM': 0.18,
        '256QAM': 0.25,
    },
    'Numerology': 1, #µ(0)=15kHz, µ(1)=30kHz, µ(2)=60kHz
    'Bandwidth': 100, #MHz (BW(j))
    'Modulation': 256, #QAM
    'Number_of_cells': 4,
    'Number_of_UEs': 64, 
    'DL': 2000, # Mbps 
    'UL': 500, # Mbps 
    'number_of_aggregated_component_carriers': 1, # (J) max = 16
    'DL_MIMO_Layers': 4, # (v(j)) max = 8 
    'UL_MIMO_Layers': 4, # (v(j)) max = 4
    'MU_MIMO':  1, # Number of Beam with MU-MIMO Users; 
    'Number_of_logical_antenna_ports': 4, # 1/2/4/8/16. Used for fronthaul throughput only, should be higher than MIMO Layers
    'Rmax': 0.92578125, # value depends on the type of coding from 3GPP 38.212 and 3GPP 38.214 (For LDPC code maximum number is 948/1024) 
    'spectral_efficiency': 7.4063, #3GPP TS 38.214 version 15.3.0 Release 15, Table 5.1.3.1-2 (256QAM)
    'Scaling_factor' : 1, # (f(j))
    'DL_UP_ratio': 0.7, #10/14, # based on slot configuration 6:4:4 (6 dl, 4 guard, 4 ul) ref: https://jira.cec.lab.emc.com/browse/MP-4406
    'IQ_mantissa_bitwidth': 8, # per I or per Q
    'IQ_exp_bitwidth': 4,
}

COSTS = {
    #all costs in $USD
    'cpu': [
        {
            'model': '6148',
            'price': 2988.39,
            'cores': 20,
            'power': 150,
        },
        {
            'model': '6230',
            'price': 1582.72,
            'cores': 26,
            'power': 150,
        },
    ],
    'switch': [
        {
            'model': '10GB Fiber',
            'price': 2000,
            'ports': 8,
            'power': 150,
            'speed': 10, #Gbps
        },
        {
            'model': '25GB Fiber',
            'price': 8000,
            'ports': 8,
            'power': 350,
            'speed': 25, #Gbps
        },
    ],
    'server': [
        {
            'model': 'XR11',
            'price': 900,
            'size': '1U',
            'power': 150,
            'cpu_max': 2,
            'pcie_max': 4,
        },
        {
            'model': 'R750',
            'price': 1700,
            'size': '2U',
            'power': 200,
            'cpu_max': 2,
            'pcie_max': 4,
        },
    ],
    'lease_line_installation': [
        {
            'model': '1Gbps',
            'price': 1000,
            'speed': 1, #Gbps
        },
        {
            'model': '10Gbps',
            'price': 2000,
            'speed': 10, #Gbps
        },        
        {
            'model': '100Gbps',
            'price': 10000,
            'speed': 100, #Gbps
        },
    ],
    'lease_line_installation_per_meter': [
        {
            'model': '1Gbps',
            'price': 0.1,
            'speed': 1, #Gbps
        },
        {
            'model': '10Gbps',
            'price': 0.2,
            'speed': 10, #Gbps
        },        
        {
            'model': '100Gbps',
            'price': 0.3,
            'speed': 100, #Gbps
        },
    ],
    'lease_line_rental': [
        {
            'model': '1Gbps',
            'price': 500,
            'speed': 1, #Gbps
        },
        {
            'model': '10Gbps',
            'price': 5000,
            'speed': 10, #Gbps
        },        
        {
            'model': '100Gbps',
            'price': 15000,
            'speed': 100, #Gbps
        },
    ],
    'sfp': [
        {
            'model': 'QSPF28',
            'price': 599, #usd
            'distance': 10000, #meters
            'speed': 100, #Gbps
        },
        {
            'model': 'SPF28',
            'price': 420, #usd
            'distance': 30000, #meters
            'speed': 25, #Gbps
        },
        {
            'model': 'Dell SPF',
            'price': 115, #usd
            'distance': 300, #meters
            'speed': 10, #Gbps
        },
    ],
    'single_sector_antenna': [
        {
            'price': 1500
        },
    ],
    'ru': [
        {
            'price': 4000
        },
    ],
    'du': [
        {
            'price': 10000
        },
    ],
    'cu': [
        {
            'price': 15000
        },
    ],
    'tower': [
        {
            'price': 10000
        },
    ],
    'transportation': [
        {
            'price': 10000
        },
    ],
    'installation': [
        {
            'price': 5000
        },
    ],
    'site_rental': [
        {
            'price': 8000
        },
    ],
    'power_generator_battery_system': [
        {
            'price': 5000
        },
    ],
    'smo': [
        {
            'price': 2000
        },
    ],    
    'l1_controller': [
        {
            'model': 'marvell',
            'price': 900,
            'ports': 4,
            'speed': 10, # Gbps
        },
    ],

}

fm = Cost(simulation_parameters = PARAMETERS, cost_parameters = COSTS)

def test_get_sites_per_km2():
    site_radius = 100 # meters
    res = fm.get_sites_per_km2(site_radius)
    print(res)
    assert res == pytest.approx(28,1)

def test_discount_ownership_cost_capex():
    cost = 1000 # usd
    res = fm.discount_ownership_cost(cost, True)
    print(res)
    assert res == pytest.approx(1860,1)   

def test_discount_ownership_cost_opex():
    cost = 1000 # usd
    res = fm.discount_ownership_cost(cost, False)
    print(res)
    assert res == pytest.approx(8607,1) 

def test_get_cost():
    res = fm.get_cost(sites_per_km2 = 12.5, capacity_gbps = 6, rudu_distance=15000, ducu_distance=10000, CUCP_utils = 50, CUUP_utils = 100, DU_utils = 150)
    print(res)
    assert len(res) >= 1

def test_cost_optimized_1():
    res = fm.cost_optimized('switch', ports=3, speed=12)
    print(res)
    assert res['price'] == 8000

def test_cost_optimized_2():
    res = fm.cost_optimized('ru')
    print(res)
    assert res['price'] == 4000


test_get_cost()