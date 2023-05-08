import matplotlib.pyplot as plt
from random_coord_generator import generate_random_points,plot_source_destination_points
from nearest_point import get_nearest_point
from plot_lines_nearest_point import plot_connected_points
from descriptive_stats import plot_distance_stats, plot_distance_comparison

from import_graphs import plot_edges,project_graph,get_graph_from_place
from import_graphs import load_graph,get_graph_from_points,save_graph
from import_graphs import get_nearest_point_graph,nodes_edges
from import_graphs import generate_random_points_from_nodes

from interactive_map import compute_all_distances_and_paths
from interactive_map import PointBrowser,PointBrowser2,PointBrowser3


graph_input = 'load'

if graph_input == 'make_city':
    #graph = get_graph_from_points(sources, destinations, network_type='walk')
    graph = get_graph_from_place("Derby, England")
    save_graph(graph, "data/graph.graphml")
elif graph_input == 'load':
    graph = load_graph("data/graph.graphml")

nodes,edges = nodes_edges(graph)


sources = generate_random_points_from_nodes(nodes,n = 1000)
destinations = generate_random_points_from_nodes(nodes,n = 5)
destinations.to_file("data/destinations_4326.gpkg", driver="GPKG")

##### generate points or import them from GIS
# generate two sets of random points

#sources = generate_random_points(n = 100)
#destinations = generate_random_points(n = 5)








##### first method: straight lines between people and destinations
# plot the initial points
fig,ax = plot_source_destination_points(sources, destinations)
edges.plot(ax=ax, color='grey', label = "Graph's edges",zorder = 0,linewidth = 0.2)
#get the closes points from each source to destination using knn
closest_points, closest_distances = get_nearest_point(sources, destinations,k_neighbors=1)

#plot nearest connected points
fig,ax = plot_connected_points(sources, closest_points, closest_distances)
edges.plot(ax=ax, color='grey', label = "Graph's edges",zorder = 0,linewidth = 0.2)
ax.tight()
#plot some descriptive stats
plot_distance_stats(closest_distances)



#### second method: shortest path between people and destinations
# plot edges and points
plot_edges(sources,destinations,graph)

#get shortest path to destinations via the graph
path_origins,path_destinations,path_distances = get_nearest_point_graph(graph, destinations, sources)

#plot nearest connected points
plot_connected_points(path_origins, path_destinations, path_distances)

#plot some descriptive stats
plot_distance_stats(path_distances)



#### comparison
# comparison of distance distribution
plot_distance_comparison(closest_distances, path_distances,
                          labels=['Straight Lines', 'Shortest Path'],
                          title='Distance Comparison: Straight Lines vs. Shortest Path')






# if __name__ == '__main__':
#     import pickle
#     compute_nodes_destinations = True
    
#     if compute_nodes_destinations:
#         graph_utm, nodes_utm, edges_utm = project_graph(graph)
#         all_distances, all_paths = compute_all_distances_and_paths(graph_utm, destinations)
#         with open('data/all_distances_and_paths.pkl', 'wb') as f:
#             pickle.dump((all_distances, all_paths), f)
#     else:
#         with open('data/all_distances_and_paths.pkl', 'rb') as f:
#             all_distances, all_paths = pickle.load(f)
    
    
    
#     fig, ax = plt.subplots(figsize=(16, 10))
#     browser = PointBrowser(all_paths, all_distances,graph,nodes,edges, destinations,ax)
#     fig.canvas.mpl_connect('motion_notify_event', browser.on_click)
    
    
#     graph_utm, nodes_utm, edges_utm = project_graph(graph)
#     dest_utm = destinations.to_crs(crs=graph_utm.graph['crs'])
#     fig, ax = plt.subplots(figsize=(16, 10))
#     point_browser = PointBrowser2(graph_utm, nodes_utm, edges_utm, dest_utm, ax=ax)
#     fig.canvas.mpl_connect('motion_notify_event', point_browser.on_click)
    
#     fig, ax = plt.subplots(figsize=(16, 10))
#     point_browser = PointBrowser3(graph_utm, dest_utm, ax=ax)
#     fig.canvas.mpl_connect('motion_notify_event', point_browser.on_click)
