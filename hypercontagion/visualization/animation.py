from collections import defaultdict

import matplotlib.pyplot as plt
import xgi
from celluloid import Camera

__all__ = ["contagion_animation"]


def contagion_animation(
    fig, H, transition_events, pos, node_colors, edge_colors, dt=1, fps=1
):
    """Generate an animation object of contagion process.

    Parameters
    ----------
    fig : figure handle
        The figure to plot onto
    H : xgi.Hypergraph
        The hypergraph on which the simulation occurs
    transition_events : list of dict
        The output of the epidemic simulation functions with `return_event_data=True`
    pos : dict of list
        a dict with node IDs as keys and [x, y] coordinates as values
    node_colors : dict of str or tuple
        a dict with state values as keys and colors as values.
    edge_colors : dict of str or tuple
        a dict with state values as keys and colors as values.
    dt : float > 0, default: 1
        the timestep at which to take snapshots of the system states
    fps : int, default: 1
        frames per second in the animation.

    Returns
    -------
    animation object
        The resulting animation
    """

    node_state = defaultdict(lambda: "S")

    camera = Camera(fig)

    event_interval_list = get_events_in_equal_time_intervals(transition_events, dt)
    for interval_time in event_interval_list:
        events = event_interval_list[interval_time]

        edge_state = defaultdict(lambda: "OFF")

        # update edge and node states
        for event in events:
            status = event["new_state"]
            source = event["source"]
            target = event["target"]
            if source is not None:
                edge_state[source] = status
            # update node states
            node_state[target] = status

        node_fc = {n: node_colors[node_state[n]] for n in H.nodes}
        edge_fc = {e: edge_colors[edge_state[e]] for e in H.edges}

        # draw hypergraph
        plt.title(f"Time is {interval_time}")
        xgi.draw(H, pos=pos, node_fc=node_fc, edge_fc=edge_fc)
        camera.snap()

    return camera.animate(interval=1000 / fps)


def get_events_in_equal_time_intervals(transition_events, dt):
    """Converts an event stream into events per time interval.

    Parameters
    ----------
    transition_events : list of dict
        output of epidemic simulations with `return_event_data=True`
    dt : float > 0
        the time interval over which to aggregate events.

    Returns
    -------
    dict of lists of dicts
        the key is the start time of the time interval and
        the values are the list of events
    """
    tmin = transition_events[0]["time"]

    new_events = defaultdict(list)

    t = tmin
    for event in transition_events:
        if event["time"] < t + dt:
            new_events[t].append(event)
        else:
            t += dt
            new_events[t].append(event)

    return new_events
