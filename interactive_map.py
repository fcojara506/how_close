
import osmnx as ox
import networkx as nx
import multiprocessing as mp
from functools import partial
from shapely.geometry import LineString
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import random

def compute_distances_and_paths_from_single_node(node_id, graph_utm, closest_target_nodes, weight):
    distances, paths = nx.single_source_dijkstra(graph_utm, node_id, weight=weight)
    # Filter the results to only include the specified destinations
    filtered_distances = {destination: distances[destination] for destination in closest_target_nodes if destination in distances}
    filtered_paths = {destination: paths[destination] for destination in closest_target_nodes if destination in paths}
    return node_id, filtered_distances, filtered_paths

def compute_all_distances_and_paths(graph_utm, destinations, weight='length'):
    print("computing all distances and paths to destinations points")
    # Reproject destinations data to UTM
    dest_utm = destinations.to_crs(crs=graph_utm.graph['crs'])
    
    # Get the closest nodes to each destination point
    closest_target_nodes = ox.distance.nearest_nodes(G=graph_utm, X=dest_utm.geometry.x, Y=dest_utm.geometry.y)

    # Partially apply the function to be parallelized with the required arguments
    compute_partial = partial(compute_distances_and_paths_from_single_node, graph_utm=graph_utm, closest_target_nodes=graph_utm.nodes, weight=weight)

    # Parallelize the calculations
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(compute_partial, closest_target_nodes)

    # Initialize dictionaries for all_distances and all_paths
    all_distances = {}
    all_paths = {}

    # Iterate over the results from the parallelized calculations
    for node_id, distances, paths in results:
        all_distances[node_id] = distances
        all_paths[node_id] = paths
        
    #inverse the order of dictionary
    all_distances = pd.DataFrame(all_distances).transpose().to_dict()
    all_paths = pd.DataFrame(all_paths).transpose().to_dict()

    return all_distances, all_paths


#plot an static map
def plot_paths_routes_one_node(all_paths, all_distances, nodes,edges,closest_target_nodes, destinations, origin_node, ax=None):
    
    if ax is None:
        fig, ax = plt.subplots()
    
    
    all_path_node = all_paths[origin_node]
    all_distances_node = all_distances[origin_node]
    
    paths = [LineString(list(nodes.loc[all_path_node[destination]].geometry.values)) for destination in all_path_node]
    # Create GeoDataFrame from paths
    routes = gpd.GeoDataFrame(geometry=paths, crs="EPSG:4326")
    
    # Create a GeoSeries for the origin geometry
    origin = gpd.GeoSeries(nodes.loc[origin_node].geometry, crs="EPSG:4326")

    ax = edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.7)
    ax = origin.plot(ax=ax, color='red', label='Origin')
    ax = destinations.plot(ax=ax, color='blue', label='Destinations')
    
    # Set up a colormap to get unique colors
    cmap = plt.cm.get_cmap('viridis', len(routes))

    # Plot each route with a different color
    for idx, route in routes.iterrows():
        color = mcolors.to_hex(cmap(idx))
        temp_gdf = gpd.GeoDataFrame({'geometry': [route['geometry']]}, crs="EPSG:4326")
        ax = temp_gdf.plot(ax=ax, linewidth=3, alpha=0.8, color=color)
        
        # Get the destination node
        dest_node = closest_target_nodes[idx]
        dest_lat, dest_lon = nodes.loc[dest_node].geometry.y, nodes.loc[dest_node].geometry.x
        distance = all_distances_node[closest_target_nodes[idx]]
        
        # Annotate the distance
        ax.annotate(
            f"{distance:.0f} m",
            xy=(dest_lon, dest_lat),
            xytext=(dest_lon - 0.001, dest_lat - 0.0015),
            arrowprops=dict(facecolor="black", arrowstyle="->"),
            fontsize=10,
            color="black"
            )
    # Put a legend below the current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=False, shadow=False, ncol=2, fontsize=13)
    plt.xlabel("lon (degrees)")
    plt.ylabel("lat (degrees)")
    
    return ax




class PointBrowser:
    def __init__(self, all_paths, all_distances, graph, nodes, edges, destinations, ax):

        self.all_distances = all_distances
        self.all_paths = all_paths
        self.graph = graph
        self.destinations = destinations
        self.ax = ax
        self.nodes = nodes
        self.edges = edges
        self.closest_target_nodes = ox.distance.nearest_nodes(G=graph, X=destinations.geometry.x, Y=destinations.geometry.y)
        
        
        self.edges.plot(ax=self.ax, color='gray', linewidth=0.5, alpha=0.7)
        self.destinations.plot(ax=self.ax, color='blue', label='Destinations')
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=False, shadow=False, ncol=2, fontsize=13)
        plt.xlabel("lon (degrees)")
        plt.ylabel("lat (degrees)")
        self.list_axes_children_before = list(self.ax.get_children())
        
        # Initial plot
        self.update_plot(origin_node=random.sample(list(nodes.index), 1)[0])
  
    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        # Find the nearest node to the click location
        clicked_point = (event.ydata, event.xdata)
        origin_node = ox.distance.nearest_nodes(self.graph, X=[clicked_point[1]], Y=[clicked_point[0]])[0]

        self.update_plot(origin_node)
        
        
    def update_plot(self, origin_node):
        
        def remove_diff_list(temp1,temp2):
            return [item.remove() for item in temp2 if item not in temp1]
        
        # Clear previous origin node and routes
        remove_diff_list(self.list_axes_children_before,list(self.ax.get_children()))
        

        self.nodes.loc[[origin_node]].plot(ax=self.ax, color='red', label='Origin')

        all_path_node = self.all_paths[origin_node]
        
        
        paths = [LineString(list(self.nodes.loc[all_path_node[destination]].geometry.values)) for destination in all_path_node]
        # Create GeoDataFrame from paths
        routes = gpd.GeoDataFrame(geometry=paths, crs="EPSG:4326")        
        # Set up a colormap to get unique colors
        cmap = plt.cm.get_cmap('viridis', len(routes))

        # Plot each route with a different color
        for idx, route in routes.iterrows():
            color = mcolors.to_hex(cmap(idx))
            temp_gdf = gpd.GeoDataFrame({'geometry': [route['geometry']]}, crs="EPSG:4326")
            temp_gdf.plot(ax=self.ax, linewidth=3, alpha=0.8, color=color)
            

            # Annotate the distance
            dest_node = self.closest_target_nodes[idx]
            dest_lat, dest_lon = self.nodes.loc[dest_node].geometry.y, self.nodes.loc[dest_node].geometry.x
            print(origin_node)
            print(dest_node)
            distance = self.all_distances[origin_node][dest_node]        
            self.ax.annotate(
            f"{distance:.0f} m",
            xy=(dest_lon, dest_lat),
            xytext=(dest_lon - 0.001, dest_lat - 0.0015),
            arrowprops=dict(facecolor="black", arrowstyle="->"),
            fontsize=10,
            color="black"
        )

class PointBrowser2:

    def __init__(self, graph_utm, nodes_utm, edges_utm, dest_utm, ax):
        self.graph = graph_utm
        self.destinations = dest_utm
        self.ax = ax
        self.nodes = nodes_utm
        self.edges = edges_utm
        self.crs  = graph_utm.graph['crs']
        self.edges.plot(ax=self.ax, color='gray', linewidth=0.5, alpha=0.7)
        self.destinations.plot(ax=self.ax, color='blue', label='Destinations')


        self.closest_target_nodes = ox.distance.nearest_nodes(G=self.graph, X=self.destinations.geometry.x, Y=self.destinations.geometry.y)
        self.list_axes_children_before = list(self.ax.get_children())

        # Initial plot
        origin_node = random.sample(list(self.nodes.index), 1)[0]
        self.update_plot(origin_node)

    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        # Find the nearest node to the click location
        clicked_point = (event.ydata, event.xdata)
        origin_node = ox.distance.nearest_nodes(self.graph, X=[clicked_point[1]], Y=[clicked_point[0]])[0]

        self.update_plot(origin_node)

    def update_plot(self, origin_node):
        def remove_diff_list(temp1, temp2):
            return [item.remove() for item in temp2 if item not in temp1]

        # Clear previous origin node and routes
        remove_diff_list(self.list_axes_children_before, list(self.ax.get_children()))

        self.nodes.loc[[origin_node]].plot(ax=self.ax, color='red', label='Origin')
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=False, shadow=False, ncol=2, fontsize=13)
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        
        node_id, filtered_distances, filtered_paths = compute_distances_and_paths_from_single_node(origin_node, self.graph, self.closest_target_nodes, weight='length')
        
        paths = [LineString(list(self.nodes.loc[filtered_paths[destination]].geometry.values)) for destination in filtered_paths]
        # Create GeoDataFrame from paths
        routes = gpd.GeoDataFrame(geometry=paths, crs= self.crs)

        # Set up a colormap to get unique colors
        cmap = plt.cm.get_cmap('viridis', len(routes))

        # Plot each route with a different color
        for idx, route in routes.iterrows():
            color = mcolors.to_hex(cmap(idx))
            temp_gdf = gpd.GeoDataFrame({'geometry': [route['geometry']]}, crs= self.crs)
            temp_gdf.plot(ax=self.ax, linewidth=3, alpha=0.8, color=color)

            # Annotate the distance
            dest_node = self.closest_target_nodes[idx]
            dest_lat, dest_lon = self.nodes.loc[dest_node].geometry.y, self.nodes.loc[dest_node].geometry.x
            distance = filtered_distances[dest_node]
            self.ax.annotate(
                f"{distance:.0f} m",
                xy=(dest_lon, dest_lat),
                xytext=(dest_lon - 0.001, dest_lat - 0.0015),
                fontsize=10,
                color="black"
            )

class PointBrowser3:

    def __init__(self, graph_utm, dest_utm, ax):
        self.graph = graph_utm
        self.destinations = dest_utm
        self.ax = ax
        self.nodes = ox.graph_to_gdfs(self.graph, edges=False)
        self.edges = ox.graph_to_gdfs(self.graph, nodes=False)
        self.crs  = graph_utm.graph['crs']
        self.edges.plot(ax=self.ax, color='gray', linewidth=0.5, alpha=0.7)
        self.destinations.plot(ax=self.ax, color='blue', label='Destinations')


        self.closest_target_nodes = ox.distance.nearest_nodes(G=self.graph, X=self.destinations.geometry.x, Y=self.destinations.geometry.y)
        self.list_axes_children_before = list(self.ax.get_children())

        # Initial plot
        origin_node = random.sample(list(self.nodes.index), 1)[0]
        self.update_plot(origin_node)

    def on_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        # Find the nearest node to the click location
        clicked_point = (event.ydata, event.xdata)
        origin_node = ox.distance.nearest_nodes(self.graph, X=[clicked_point[1]], Y=[clicked_point[0]])[0]

        self.update_plot(origin_node)

    def update_plot(self, origin_node):
        def remove_diff_list(temp1, temp2):
            return [item.remove() for item in temp2 if item not in temp1]

        # Clear previous origin node and routes
        remove_diff_list(self.list_axes_children_before, list(self.ax.get_children()))

        self.nodes.loc[[origin_node]].plot(ax=self.ax, color='red', label='Origin')
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=False, shadow=False, ncol=2, fontsize=13)
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")
        
        node_id, filtered_distances, filtered_paths = compute_distances_and_paths_from_single_node(origin_node, self.graph, self.closest_target_nodes, weight='length')
        
        paths = [LineString(list(self.nodes.loc[filtered_paths[destination]].geometry.values)) for destination in filtered_paths]
        # Create GeoDataFrame from paths
        routes = gpd.GeoDataFrame(geometry=paths, crs= self.crs)

        # Set up a colormap to get unique colors
        cmap = plt.cm.get_cmap('viridis', len(routes))

        # Plot each route with a different color
        for idx, route in routes.iterrows():
            color = mcolors.to_hex(cmap(idx))
            temp_gdf = gpd.GeoDataFrame({'geometry': [route['geometry']]}, crs= self.crs)
            temp_gdf.plot(ax=self.ax, linewidth=3, alpha=0.8, color=color)

            # Annotate the distance
            dest_node = self.closest_target_nodes[idx]
            dest_lat, dest_lon = self.nodes.loc[dest_node].geometry.y, self.nodes.loc[dest_node].geometry.x
            distance = filtered_distances[dest_node]
            self.ax.annotate(
                f"{distance:.0f} m",
                xy=(dest_lon, dest_lat),
                xytext=(dest_lon - 0.001, dest_lat - 0.0015),
                fontsize=10,
                color="black"
            )


