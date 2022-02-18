import networkx as nx
import xgi


def get_spring_layout(H):
    G, node_dict, edge_dict = xgi.to_bipartite_network(H)
    pos = nx.spring_layout(G)

    node_pos = dict()
    edge_pos = dict()

    for id, coords in pos.items():
        if G.nodes[id]["bipartite"] == 0:
            node_pos[node_dict[id]] = coords
        else:
            edge_pos[edge_dict[id]] = coords

    return node_pos, edge_pos


def get_stylized_hypergraph(H):

    node_pos, edge_pos = get_spring_layout(H)
    stylized_hypergraph = dict()

    stylized_hypergraph["width"] = 548
    stylized_hypergraph["height"] = 548
    stylized_hypergraph["link_color"] = "#7c7c7c"
    stylized_hypergraph["link_alpha"] = 0.5
    stylized_hypergraph["node_stroke_color"] = "#555555"
    stylized_hypergraph["node_stroke_width"] = 0.9493368677316703

    stylized_hypergraph["nodes"] = list()
    stylized_hypergraph["hyperedges"] = list()
    stylized_hypergraph["bipartite_edges"] = list()

    for node in H.nodes:
        stylized_hypergraph["nodes"].append(
            {
                "id": node,
                "x_canvas": node_pos[node][0],
                "y_canvas": node_pos[node][1],
                "radius": 1.7,
                "color": "#79aaa0",
            }
        )
    for edge in H.edges:
        stylized_hypergraph["hyperedges"].append(
            {
                "id": edge,
                "x_canvas": edge_pos[edge][0],
                "y_canvas": node_pos[edge][1],
                "radius": 1.7,
                "color": "#79aaa0",
            }
        )

    for node in H.nodes:
        for edge in H.nodes.memberships(node):
            stylized_hypergraph["bipartite_edges"].append(
                {"source": node, "target": edge, "width": 1.6, "color": "#7c7c7c"}
            )

    return stylized_hypergraph
