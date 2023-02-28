import sys
print(sys.executable)
from mpa_sim.services.fronthaul import fronthaul_sim

import sys

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
    'signaling_overhead': 0.18,
    'modulation_compression': True,
    'compression_ratio': {
        'QPSK': 0.06,
        '16QAM': 0.12,
        '64QAM': 0.18,
        '256QAM': 0.25,
    },
}

fm = fronthaul_sim(PARAMETERS)

def test_estimate_fronthaul_capacity_qpsk():
    assert fm.estimate_fronthaul_capacity(50, "QPSK") == 3.0

def test_estimate_fronthaul_capacity_None():
    assert fm.estimate_fronthaul_capacity(50.0, None) == 50.0

def test_estimate_fronthaul_capacity_256qam():
    assert fm.estimate_fronthaul_capacity(5.4, "256QAM") == 1.35

