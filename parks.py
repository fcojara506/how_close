import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt

# get all building footprints in some neighborhood
# `True` means retrieve any object with this tag, regardless of value
place = "Derby,England"
tags = {"leisure": ["park","nature_reserve"]}
gdf = ox.geometries_from_place(place, tags)


def load_graph(filename):
    return ox.load_graphml(filename)

graph = load_graph("data/graph.graphml")

nodes = ox.graph_to_gdfs(graph, edges=False)
edges = ox.graph_to_gdfs(graph, nodes=False)

fig, ax = plt.subplots()
edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.7)
gdf.plot(ax=ax)
