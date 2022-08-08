"""
Contains useful classes and functions for use in the hypercontagion library.
"""

import heapq
import random
from collections import Counter, defaultdict

import numpy as np

__all__ = [
    "EventQueue",
    "MockSamplableSet",
    "SamplingDict",
    "_process_trans_SIR_",
    "_process_rec_SIR_",
    "_process_trans_SIS_",
    "_process_rec_SIS_",
]


class EventQueue:
    r"""
    This class is used to store and act on a priority queue of events for
    event-driven simulations.  It is based on heapq.
    Each queue is given a tmax (default is infinity) so that any event at later
    time is ignored.

    This is a priority queue of 4-tuples of the form
                   ``(t, counter, function, function_arguments)``
    The ``'counter'`` is present just to break ties, which generally only occur when
    multiple events are put in place for the initial condition, but could also
    occur in cases where events tend to happen at discrete times.
    note that the function is understood to have its first argument be t, and
    the tuple ``function_arguments`` does not include this first t.
    So function is called as
        ``function(t, *function_arguments)``
    Previously I used a class of events, but sorting using the __lt__ function
    I wrote was significantly slower than simply using tuples.
    """

    def __init__(self, tmax=float("Inf")):
        self._Q_ = []
        self.tmax = tmax
        self.counter = 0  # tie-breaker for putting things in priority queue

    def add(self, time, function, args=()):
        """Add event to the queue.

        Parameters
        ----------
        time : float
            time of the event
        function : function name
            name of the function to run when the event is popped.
        args : keyword args
            args of the function excluding time.
        """
        if time < self.tmax:
            heapq.heappush(self._Q_, (time, self.counter, function, args))
            self.counter += 1

    def pop_and_run(self):
        """Pops the next event off the queue and performs the function"""
        t, counter, function, args = heapq.heappop(self._Q_)
        function(t, *args)

    def __len__(self):
        """this allows us to use commands like ``while Q:``

        Returns
        -------
        int
            number of events currently in the queue
        """
        return len(self._Q_)


class SamplingDict:
    """
    The Gillespie algorithm will involve a step that samples a random element
    from a set based on its weight.  This is awkward in Python.

    So I'm introducing a new class based on a stack overflow answer by
    Amber (http://stackoverflow.com/users/148870/amber)
    for a question by
    tba (http://stackoverflow.com/users/46521/tba)
    found at
    http://stackoverflow.com/a/15993515/2966723

    This will allow selecting a random element uniformly, and then use
    rejection sampling to make sure it's been selected with the appropriate
    weight.
    """

    def __init__(self, weighted=False):
        self.item_to_position = {}
        self.items = []

        self.weighted = weighted
        if self.weighted:
            self.weight = defaultdict(int)  # presume all weights positive
            self.max_weight = 0
            self._total_weight = 0
            self.max_weight_count = 0

    def __len__(self):
        """Number of items in the dict

        Returns
        -------
        int
            number of items in dict
        """
        return len(self.items)

    def __contains__(self, item):
        """Whether an item exists in the dictionary"""
        return item in self.item_to_position

    def _update_max_weight(self):
        """Internal function to help with the rejection sampling"""
        C = Counter(
            self.weight.values()
        )  # may be a faster way to do this, we only need to count the max.
        self.max_weight = max(C.keys())
        self.max_weight_count = C[self.max_weight]

    def insert(self, item, weight=None):
        """insert an item into the sampling dict

        Parameters
        ----------
        item : hashable
            the ID of the item
        weight : float, default: None
            the weight of the item, if None, unweighted.

        Notes
        -----
        If not present, then inserts the thing (with weight if appropriate)
        if already there, replaces the weight unless weight is 0

        If weight is 0, then it removes the item and doesn't replace.

        replaces weight if already present, does not increment weight.
        """

        if self.__contains__(item):
            self.remove(item)
        if weight != 0:
            self.update(item, weight_increment=weight)

    def update(self, item, weight_increment=None):
        """_summary_

        Parameters
        ----------
        item : hashable
            ID of the item
        weight_increment : float, default: None
            how much to increment the weight if weighted.

        Raises
        ------
        Exception
            if weighted and no weight increment specified.

        Notes
        -----
        If not present, then inserts the item (with weight if appropriate)
        if already there, increments weight

        increments weight if already present, cannot overwrite weight.
        """
        if (
            weight_increment is not None
        ):  # will break if passing a weight to unweighted case
            if weight_increment > 0 or self.weight[item] != self.max_weight:
                self.weight[item] = self.weight[item] + weight_increment
                self._total_weight += weight_increment
                if self.weight[item] > self.max_weight:
                    self.max_weight_count = 1
                    self.max_weight = self.weight[item]
                elif self.weight[item] == self.max_weight:
                    self.max_weight_count += 1
            else:  # it's a negative increment and was at max
                self.max_weight_count -= 1
                self.weight[item] = self.weight[item] + weight_increment
                self._total_weight += weight_increment
                self.max_weight_count -= 1
                if self.max_weight_count == 0:
                    self._update_max_weight
        elif self.weighted:
            raise Exception("if weighted, must assign weight_increment")

        if item in self:  # we've already got it, do nothing else
            return
        self.items.append(item)
        self.item_to_position[item] = len(self.items) - 1

    def remove(self, choice):
        """Remove item and update weights

        Parameters
        ----------
        choice : hashable
            item ID
        """
        position = self.item_to_position.pop(
            choice
        )  # why don't we pop off the last item and put it in the choice index?
        last_item = self.items.pop()
        if position != len(self.items):
            self.items[position] = last_item
            self.item_to_position[last_item] = position

        if self.weighted:
            weight = self.weight.pop(choice)
            self._total_weight -= weight
            if weight == self.max_weight:
                # if we find ourselves in this case often
                # it may be better just to let max_weight be the
                # largest weight *ever* encountered, even if all remaining weights are less
                #
                self.max_weight_count -= 1
                if self.max_weight_count == 0 and len(self) > 0:
                    self._update_max_weight()

    def choose_random(self):
        """chooses a random node.  If there is a weight, it will use rejection
        sampling to choose a random node until it succeeds"""
        if self.weighted:
            while True:
                choice = random.choice(self.items)
                if random.random() < self.weight[choice] / self.max_weight:
                    break
            return choice

        else:
            return random.choice(self.items)

    def random_removal(self):
        """uses other class methods to choose and then remove a random item"""
        choice = self.choose_random()
        self.remove(choice)
        return choice

    def total_weight(self):
        """Get the sum of all the weights in the dict."""
        if self.weighted:
            return self._total_weight
        else:
            return len(self)

    def update_total_weight(self):
        """Update the sum of weights."""
        self._total_weight = sum(self.weight[item] for item in self.items)


def choice(arr, p):
    """
    Returns a random element from ``arr`` with probability given in array ``p``.
    If ``arr`` is not an iterable, the function returns the index of the chosen element.
    """
    ndx = np.argmax(np.random.rand() < np.cumsum(p))
    try:
        return arr[ndx]
    except TypeError as e:
        return ndx


class MockSamplableSet:
    """
    A set of items that can be sampled with probability
    proportional to a corresponding item weight.

    Mimicks the behavior of github.com/gstonge/SamplableSet
    without being as efficient.

    Works similar to Python's set, with ``__getitem__``,
    ``__setitem__``, ``__delitem__``, ``__iter__``,
    ``__len__``, ``__contains__``.

    Parameters
    ==========
    min_weight : float
        minimum possible weight
    max_weight : float
        maximum possible weight
    weighted_elements : list, default = []
        list of 2-tuples, first entry an item, second entry a weight
    cpp_type : str, default = 'int'
        The type of the items.

    Attributes
    ==========
    min_weight : float
        minimum possible weight
    max_weight : float
        maximum possible weight
    items : numpy.ndarray
        list of items in this set
    weights : numpy.ndarray
        list of corresponding weights
    """

    def __init__(self, min_weight, max_weight, weighted_elements=[], cpp_type="int"):

        self.min_weight = min_weight
        self.max_weight = max_weight

        if type(weighted_elements) == dict:
            weighted_elements = list(weighted_elements.items())

        self.items = np.array([e[0] for e in weighted_elements], dtype=cpp_type)
        self.weights = np.array([e[1] for e in weighted_elements], dtype=float)
        sort_ndx = np.argsort(self.items)
        self.items = self.items[sort_ndx]
        self.weights = self.weights[sort_ndx]
        self._total_weight = self.weights.sum()

        if np.any(self.weights < self.min_weight):
            raise ValueError("There are weights below the limit.")

        if np.any(self.weights > self.max_weight):
            raise ValueError("There are weights above the limit.")

    def sample(self):
        """
        Random sample from the set, sampled
        with probability proportional to items' weight.

        Returns
        =======
        item : cpp_type
            An item from the set
        weight : float
            The weight of the item
        """

        # ndx = np.random.choice(len(self.items),p=self.weights/self._total_weight)
        # ndx = np.argwhere(np.random.rand()<np.cumsum(self.weights/self._total_weight))[0][0]
        ndx = choice(len(self.items), p=self.weights / self._total_weight)
        return self.items[ndx], self.weights[ndx]

    def __getitem__(self, key):
        found_key, ndx = self._find_key(key)
        if not found_key:
            raise KeyError("`", key, "` is not in this set.")
        else:
            return self.weights[ndx]

    def __delitem__(self, key):
        found_key, ndx = self._find_key(key)
        if found_key:
            self.items = np.delete(self.items, ndx)
            self.weights = np.delete(self.weights, ndx)
            self._total_weight = self.weights.sum()

    def __setitem__(self, key, value):
        if value < self.min_weight or value > self.max_weight:
            raise ValueError(
                "Inserting element-weight pair "
                + str(key)
                + " "
                + str(value)
                + " \n"
                + "has weight value out of bounds of "
                + str(self.min_weight)
                + " "
                + str(self.max_weight)
            )
        found_key, ndx = self._find_key(key)
        if not found_key:
            self.items = np.insert(self.items, ndx, key)
            self.weights = np.insert(self.weights, ndx, value)
        else:
            self.weights[ndx] = value

        self._total_weight = self.weights.sum()

    def _find_key(self, key):
        ndx = np.searchsorted(self.items, key)
        return (not ((ndx == len(self.items) or self.items[ndx] != key)), ndx)

    def __iter__(self):
        self._ndx = 0
        return self

    def __next__(self):
        if self._ndx < len(self.items):
            i, w = self.items[self._ndx], self.weights[self._ndx]
            self._ndx += 1
            return (i, w)
        else:
            raise StopIteration

    def __len__(self):
        return len(self.items)

    def __contains__(self, key):
        return self._find_key(key)[0]

    def total_weight(self):
        """Obtain the total weight of the set"""
        return self._total_weight

    def clear(self):
        """Reset the set. Not implemented yet."""
        pass


def _process_trans_SIR_(
    t,
    times,
    S,
    I,
    R,
    Q,
    H,
    status,
    transmission_function,
    gamma,
    tau,
    source,
    target,
    rec_time,
    pred_inf_time,
    events,
):

    if status[target] == "S":  # nothing happens if already infected.
        status[target] = "I"
        times.append(t)
        events.append(
            {
                "time": t,
                "source": source,
                "target": target,
                "old_state": "S",
                "new_state": "I",
            }
        )
        S.append(S[-1] - 1)  # one less susceptible
        I.append(I[-1] + 1)  # one more infected
        R.append(R[-1])  # no change to recovered

        rec_time[target] = t + rec_delay(gamma)
        if rec_time[target] < Q.tmax:
            Q.add(
                rec_time[target],
                _process_rec_SIR_,
                args=(times, S, I, R, status, target, events),
            )

        for edge_id in H.nodes.memberships(target):
            edge = H.edges.members(edge_id)
            for nbr in edge:
                if status[nbr] == "S":
                    inf_time = t + trans_delay(tau, edge)

                    # create statuses at the time requested
                    temp_status = defaultdict(lambda: "R")
                    for node in edge:
                        if status[node] == "I" and rec_time[node] > inf_time:
                            temp_status[node] = "I"
                        elif status[node] == "S":
                            temp_status[node] = "S"

                        contagion = transmission_function(nbr, temp_status, edge)
                        if contagion != 0 and inf_time < pred_inf_time[nbr]:
                            Q.add(
                                inf_time,
                                _process_trans_SIR_,
                                args=(
                                    times,
                                    S,
                                    I,
                                    R,
                                    Q,
                                    H,
                                    status,
                                    transmission_function,
                                    gamma,
                                    tau,
                                    edge_id,
                                    nbr,
                                    rec_time,
                                    pred_inf_time,
                                    events,
                                ),
                            )
                            pred_inf_time[nbr] = inf_time


def _process_rec_SIR_(t, times, S, I, R, status, node, events):
    times.append(t)
    events.append(
        {"time": t, "source": None, "target": node, "old_state": "I", "new_state": "R"}
    )
    S.append(S[-1])  # no change to number susceptible
    I.append(I[-1] - 1)  # one less infected
    R.append(R[-1] + 1)  # one more recovered
    status[node] = "R"


def _process_trans_SIS_(
    t,
    times,
    S,
    I,
    Q,
    H,
    status,
    transmission_function,
    gamma,
    tau,
    source,
    target,
    rec_time,
    pred_inf_time,
    events,
):

    if status[target] == "S":
        status[target] = "I"
        events.append(
            {
                "time": t,
                "source": source,
                "target": target,
                "old_state": "S",
                "new_state": "I",
            }
        )
        I.append(I[-1] + 1)  # one more infected
        S.append(S[-1] - 1)  # one less susceptible
        times.append(t)

        rec_time[target] = t + rec_delay(gamma)

        if rec_time[target] < Q.tmax:
            Q.add(
                rec_time[target],
                _process_rec_SIS_,
                args=(times, S, I, status, target, events),
            )

        for edge_id in H.nodes.memberships(target):
            edge = H.edges.members(edge_id)
            for nbr in edge:
                if status[nbr] == "S":
                    inf_time = t + trans_delay(tau, edge)

                    # create statuses at the time requested
                    temp_status = defaultdict(lambda: "S")
                    for node in edge:
                        if status[node] == "I" and rec_time[node] >= inf_time:
                            temp_status[node] = "I"

                        contagion = transmission_function(nbr, temp_status, edge)
                        if contagion != 0 and inf_time < pred_inf_time[nbr]:
                            Q.add(
                                inf_time,
                                _process_trans_SIS_,
                                args=(
                                    times,
                                    S,
                                    I,
                                    Q,
                                    H,
                                    status,
                                    transmission_function,
                                    gamma,
                                    tau,
                                    edge_id,
                                    nbr,
                                    rec_time,
                                    pred_inf_time,
                                    events,
                                ),
                            )
                            pred_inf_time[nbr] = inf_time


def _process_rec_SIS_(t, times, S, I, status, node, events):
    times.append(t)
    events.append(
        {"time": t, "source": None, "target": node, "old_state": "I", "new_state": "S"}
    )
    S.append(S[-1] + 1)  # one more susceptible
    I.append(I[-1] - 1)  # one less infected
    status[node] = "S"


def rec_delay(rate):
    try:
        return random.expovariate(rate)
    except:
        return float("Inf")


def trans_delay(tau, edge):
    try:
        return random.expovariate(tau[len(edge)])
    except ZeroDivisionError:
        return np.inf
