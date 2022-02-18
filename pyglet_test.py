from networkx.generators.classic import circular_ladder_graph
import pyglet
from pyglet.window import key
from pyglet.window import mouse
import hypercontagion.visualization.draw as draw
import networkx as nx
import random
import pyglet.shapes as shapes
import xgi
import random

n = 100
m = 100
H = xgi.Hypergraph([random.sample(range(n), random.randint(2, 5)) for i in range(m)])

window = pyglet.window.Window()

node_pos = dict()
for node in H.nodes:
    node_pos[node] = [480 * random.random(), 640 * random.random()]
edge_pos = dict()
for edge in H.edges:
    edge_pos[edge] = [480 * random.random(), 640 * random.random()]

batch, nodes = draw.draw_hypergraph(H, node_pos, edge_pos)


@window.event
def on_draw():
    window.clear()
    batch.draw()


# pyglet.clock.schedule(update, dt=0.1)

# @window.event
# def on_key_press(symbol, modifiers):
#     if symbol == key.A:
#         print('The "A" key was pressed.')
#     elif symbol == key.LEFT:
#         print('The left arrow key was pressed.')
#     elif symbol == key.ENTER:
#         print('The enter key was pressed.')

# event_logger = pyglet.window.event.WindowEventLogger()
# window.push_handlers(event_logger)
pyglet.app.run()
