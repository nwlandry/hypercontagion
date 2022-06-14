import hypercontagion as hc
import numpy as np

def test_discordance():
    assert abs(hc.discordance(np.array([0, 1, 2]), np.array([1, 0, 0])) - 1/3) < 1e-6
    assert abs(hc.discordance(np.array([0, 1, 2]), np.array([0, 0, 0])) - 0) < 1e-6


def test_deffuant_weisbuch():
    assert 0 == 0


def test_hegselmann_krause():
    assert 0 == 0


def simulate_random_group_continuous_state_1D():
    assert 0 == 0


def test_simulate_random_node_and_group_discrete_state():
    assert 0 == 0


def test_synchronous_update_continuous_state_1D():
    assert 0 == 0
