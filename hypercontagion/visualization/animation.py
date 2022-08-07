from collections import defaultdict

import matplotlib.pyplot as plt
import xgi
from celluloid import Camera

__all__ = ["contagion_animation"]


def contagion_animation(
    fig, H, transition_events, pos, node_colors, edge_colors, dt=1, fps=1
):

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
