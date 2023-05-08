import matplotlib.pyplot as plt
import osmnx as ox
from interactive_map import PointBrowser3
import geopandas as gpd
from shiny import App, ui


def load_graph(filename):
    return ox.load_graphml(filename)

graph_utm= load_graph("data/graph_utm.graphml")
dest_utm = gpd.read_file("data/destinations_4326.gpkg").to_crs(crs=graph_utm.graph['crs'])


fig, ax = plt.subplots(figsize=(16, 10))
point_browser = PointBrowser3(graph_utm, dest_utm, ax=ax)
fig.canvas.mpl_connect('button_press_event', point_browser.on_click)

