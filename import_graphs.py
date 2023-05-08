import pandas as pd
import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import random


def get_graph_from_points(src_points, dest_points, network_type='walk'):
    bbox = pd.concat([src_points, dest_points]).total_bounds
    graph = ox.graph_from_bbox(bbox[3], bbox[1], bbox[2], bbox[0], network_type=network_type, simplify=False)
    return graph
def get_graph_from_place(name, network_type='walk'):
    graph = ox.graph_from_place(name, network_type=network_type, simplify=True)
    return graph

def nodes_edges(graph):
    # Get edges from the graph
    edges = ox.graph_to_gdfs(graph, nodes=False)
    # Get nodes from the graph
    nodes = ox.graph_to_gdfs(graph, edges=False)
    return nodes,edges

def project_graph(graph):
    graph = ox.project_graph(graph)
    # Get the GeoDataFrame
    edges = ox.graph_to_gdfs(graph, nodes=False)
    # Get nodes from the graph
    nodes = ox.graph_to_gdfs(graph, edges=False)
    return graph,nodes,edges

def save_graph(graph,filename):
    ox.save_graphml(graph,filename)

def load_graph(filename):
    return ox.load_graphml(filename)

def generate_random_points_from_nodes(nodes,n=100):
    random.seed(100)
    idx = random.sample(list(nodes.index), n)
    return gpd.GeoSeries(nodes.loc[idx].geometry).reset_index(drop=True)




def get_nearest_point_graph(graph, destinations, sources):
    # Project graph to UTM for metric measurements
    graph_proj, nodes_proj, edges_proj = project_graph(graph)
    
    # Get UTM coordinates
    CRS_utm = nodes_proj.crs
    
    # Reproject sources and destinations data to UTM
    src_utm = sources.to_crs(crs=CRS_utm)
    dest_utm = destinations.to_crs(crs=CRS_utm)
    
    # Get the closest nodes to each source and destination point
    closest_target_nodes = ox.distance.nearest_nodes(G=graph_proj, X=dest_utm.geometry.x, Y=dest_utm.geometry.y)
    closest_sources_nodes = ox.distance.nearest_nodes(G=graph_proj, X=src_utm.geometry.x, Y=src_utm.geometry.y)
    
    # Create DataFrames for sources and destinations with corresponding nodes
    sources_df = pd.DataFrame({'source_coords': sources, 'source_node': closest_sources_nodes})
    destinations_df = pd.DataFrame({'destination_coords': destinations, 'destination_node': closest_target_nodes})
    
    
    # Get the shortest path based on the target_destinations
    path_length, path_nodes = nx.multi_source_dijkstra(graph_proj, closest_target_nodes, weight='length')
    
    # Extract path nodes
    destination_node, origin_node = zip(*[(path[0], path[-1]) for path in path_nodes.values()])
    
    # Create a DataFrame from path
    path_data = pd.DataFrame({"source_node": origin_node, 'destination_node': destination_node, "distance": list(path_length.values())})
    
    # Merge DataFrames
    df = pd.merge(destinations_df,path_data, on='destination_node')
    df = pd.merge(sources_df,df, on='source_node',sort=False,how='left')

    

    origin_points = gpd.GeoSeries(df['source_coords'])
    destination_points = gpd.GeoSeries(df['destination_coords'])
    closest_distances = df['distance']

    return origin_points,destination_points,closest_distances


# # get the graph using the limits of the points
# graph= get_graph_from_points(src_gdf, dest_gdf)

def plot_edges(sources,destinations,graph):
    
    fig, ax = plt.subplots(1, figsize=(6,6),frameon=True)
    plt.title('Graph')


    gdf_edges = ox.graph_to_gdfs(graph, nodes=False)["geometry"]
    gdf_edges.plot(ax=ax, color='grey', label = "Graph's edges")
    
    
    # Plot the points
    sources.plot(color='blue',ax=ax, label='Source',markersize=1)
    destinations.plot(color='red', ax=ax, label='Destinations',markersize=300,marker = "x")
    
    #axis  
    plt.xlabel("lon (degrees)")
    plt.ylabel("lat (degrees)")
    
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=False, shadow=False, ncol=2,fontsize = 13)
            
    plt.show()
    







