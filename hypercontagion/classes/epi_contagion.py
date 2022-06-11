import networkx as nx

from hypercontagion.exception import HyperContagionError


class DiscreteStochasticEpiModel:
    def __init__(self):
        self.transition_network = nx.DiGraph()
        self.hypergraph = None
        self.state = None

    def add_transition_process(self, start_state, end_state, transition_function):
        self.transition_network.add_edge(
            start_state, end_state, function=transition_function
        )

    def add_hypergraph(self, H):
        self.hypergraph = H

    def set_initial_state(self, state):
        self.state = state

    def remaining_transitions(self, state_dict):
        num_trans = 0
        for state in state_dict:
            if self.transition_network.out_degree(state) > 0:
                num_trans += state_dict[state][-1]
        return num_trans

    def simulate(self, tmin, tmax, dt=1):
        state = dict(self.state)
        if self.state is None:
            raise HyperContagionError("Initial state was never set!")
        else:
            state_dict = dict(self.state)

        state_dict = dict()
        for s in self.transition_network.nodes:
            state_dict[s] = [0]

        for s in list(state.values()):
            state_dict[s][-1] += 1

        t = tmin
        time = [t]

        new_state = state

        while t <= tmax and self.remaining_transitions(state_dict) != 0:
            for s in self.transition_network.nodes:
                state_dict[s].append(state_dict[s][-1])

            for node in self.hypergraph.nodes:
                u = state[node]
                for v in self.transition_network.neighbors(u):
                    if self.transition_network.edges((u, v)).function:
                        new_state[node] = v

            t += dt


# # assumes all transitions are Markovian
# class GillespieStochasticEpiModel:
#     def __init__(self):
#         self.simulate = False
#         self.rates = dict()
#         self.transition_functions = dict()
#         self.hypergraph = None

#     def add_transition_process(self, start_state, end_state, transition_function):
#         self.rates[(start_state, end_state)] = SamplingDict(weighted=True)
#         self.transition_functions[(start_state, end_state)] = transition_function

#     def add_hypergraph(self, H):
#         self.hypergraph = H

#     # def simulate(tmin, tmax, return_events):
