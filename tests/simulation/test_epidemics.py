import numpy as np
import xgi

import hypercontagion as hc
from hypercontagion.simulation.functions import threshold


def test_discrete_SIR(edgelist1):
    H = xgi.Hypergraph(edgelist1)

    tmin = 10
    tmax = 20
    dt = 0.1
    gamma = 1
    tau = {1: 10, 2: 10, 3: 10}
    t, S, I, R = hc.discrete_SIR(
        H, tau, gamma, initial_infecteds=[4], tmin=tmin, tmax=tmax, dt=dt
    )

    assert np.all(S + I + R == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert abs((t[1] - t[0]) - dt) < 1e-10
    assert S[-1] == H.num_nodes - 1
    assert I[-1] == 0
    assert R[-1] == 1

    gamma = 0
    t, S, I, R = hc.discrete_SIR(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax, dt=dt, threshold=0.5
    )

    assert np.all(S + I + R == H.num_nodes)
    assert S[-1] == 4
    assert I[-1] == 4
    assert R[-1] == 0


def test_discrete_SIS(edgelist1):
    H = xgi.Hypergraph(edgelist1)

    tmin = 10
    tmax = 20
    dt = 0.1
    gamma = 1
    tau = {1: 10, 2: 10, 3: 10}
    t, S, I = hc.discrete_SIS(
        H, tau, gamma, initial_infecteds=[4], tmin=tmin, tmax=tmax, dt=dt
    )

    assert np.all(S + I == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert abs((t[1] - t[0]) - dt) < 1e-10
    assert S[-1] == H.num_nodes
    assert I[-1] == 0

    gamma = 0
    t, S, I = hc.discrete_SIS(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax, dt=dt, threshold=0.5
    )

    assert np.all(S + I == H.num_nodes)
    assert S[-1] == 4
    assert I[-1] == 4


def test_Gillespie_SIR(edgelist1):
    H = xgi.Hypergraph(edgelist1)

    tmin = 10
    tmax = 20

    gamma = 10
    tau = {1: 10, 2: 10, 3: 10}
    t, S, I, R = hc.Gillespie_SIR(
        H, tau, gamma, initial_infecteds=[4], tmin=tmin, tmax=tmax
    )

    assert np.all(S + I + R == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 0
    assert R[-1] == 1

    gamma = 0

    t, S, I, R = hc.Gillespie_SIR(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax, threshold=0.5
    )

    assert np.all(S + I + R == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 4
    assert R[-1] == 0


def test_Gillespie_SIS(edgelist1):
    H = xgi.Hypergraph(edgelist1)

    tmin = 10
    tmax = 30

    gamma = 0
    tau = {1: 10, 2: 10, 3: 10}
    t, S, I = hc.Gillespie_SIS(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax, threshold=0.5
    )

    assert np.all(S + I == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 4

    t, S, I = hc.Gillespie_SIS(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax, threshold=0.51
    )

    assert I[-1] == 2

    gamma = 100
    tau = {1: 0, 2: 0, 3: 0}
    t, S, I = hc.Gillespie_SIS(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax
    )

    assert np.all(S + I == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert S[-1] == H.num_nodes


def test_event_driven_SIR(edgelist1):
    H = xgi.Hypergraph(edgelist1)

    tmin = 10
    tmax = 20

    gamma = 10
    tau = {1: 10, 2: 10, 3: 10}
    t, S, I, R = hc.event_driven_SIR(
        H, tau, gamma, initial_infecteds=[4], tmin=tmin, tmax=tmax
    )

    assert np.all(S + I + R == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 0
    assert R[-1] == 1

    gamma = 0
    t, S, I, R = hc.event_driven_SIR(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax
    )

    assert np.all(S + I + R == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 4
    assert R[-1] == 0

    gamma = 100
    tau = {1: 0, 2: 0, 3: 0}
    t, S, I, R = hc.event_driven_SIR(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax
    )

    assert S[-1] == H.num_nodes - 1
    assert R[-1] == 1


def test_event_driven_SIS(edgelist1):
    H = xgi.Hypergraph(edgelist1)

    tmin = 10
    tmax = 20

    gamma = 10
    tau = {1: 0, 2: 0, 3: 0}
    t, S, I = hc.event_driven_SIS(
        H, tau, gamma, initial_infecteds=[4], tmin=tmin, tmax=tmax
    )

    assert np.all(S + I == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 0

    gamma = 0
    tau = {1: 10, 2: 10, 3: 10}
    t, S, I = hc.event_driven_SIS(
        H, tau, gamma, initial_infecteds=[6], tmin=tmin, tmax=tmax
    )

    assert np.all(S + I == H.num_nodes)
    assert np.min(t) == tmin
    assert np.max(t) < tmax
    assert I[-1] == 4
