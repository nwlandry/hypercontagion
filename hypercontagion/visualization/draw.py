import networkx as nx
import pyglet
import pyglet.shapes as shapes
import xgi


def draw_network(network, node_positions):
    batch = pyglet.graphics.Batch()
    net_vis = list()
    for node in network:
        x = node_positions[node][0]
        y = node_positions[node][1]
        net_vis.append(
            shapes.Circle(x=x, y=y, radius=1, color=(255, 0, 255), batch=batch)
        )

    for edge in network.edges:
        node1 = edge[0]
        node2 = edge[1]
        x1 = node_positions[node1][0]
        y1 = node_positions[node1][1]
        x2 = node_positions[node2][0]
        y2 = node_positions[node2][1]
        net_vis.append(shapes.Line(x1, y1, x2, y2, color=(255, 255, 255), batch=batch))

    return batch, net_vis


def draw_hypergraph(H, node_positions, edge_positions):
    batch = pyglet.graphics.Batch()
    vis = list()
    for node_id in H:
        x = node_positions[node_id][0]
        y = node_positions[node_id][1]
        vis.append(shapes.Circle(x=x, y=y, radius=5, color=(255, 0, 255), batch=batch))

    for edge_id in H.edges:
        x = edge_positions[edge_id][0]
        y = edge_positions[edge_id][1]
        vis.append(
            shapes.Rectangle(
                x=x, y=y, width=10, height=10, color=(0, 255, 0), batch=batch
            )
        )
    # draw bipartite edges
    for edge_id in H.edges:
        edge = H.edges[edge_id]

        x1 = edge_positions[edge_id][0]
        y1 = edge_positions[edge_id][1]
        for node_id in edge:
            x2 = node_positions[node_id][0]
            y2 = node_positions[node_id][1]
        vis.append(
            shapes.Line(x1, y1, x2, y2, color=(255, 255, 255), batch=batch, width=5)
        )

    return batch, vis
