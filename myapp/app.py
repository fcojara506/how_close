import random
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from shapely.geometry import LineString



def compute_distances_and_paths_from_single_node(node_id, graph_utm, closest_target_nodes, weight):
    distances, paths = nx.single_source_dijkstra(graph_utm, node_id, weight=weight)
    # Filter the results to only include the specified destinations
    filtered_distances = {destination: distances[destination] for destination in closest_target_nodes if destination in distances}
    filtered_paths = {destination: paths[destination] for destination in closest_target_nodes if destination in paths}
    return node_id, filtered_distances, filtered_paths


def load_graph(filename):
    return ox.load_graphml(filename)

graph_utm = load_graph("graph_utm.graphml")
dest_utm = gpd.read_file("destinations_4326.gpkg").to_crs(crs=graph_utm.graph['crs'])
nodes = ox.graph_to_gdfs(graph_utm, edges=False)
edges = ox.graph_to_gdfs(graph_utm, nodes=False)
closest_target_nodes = ox.distance.nearest_nodes(G=graph_utm, X=dest_utm.geometry.x, Y=dest_utm.geometry.y)

fig, ax = plt.subplots()
crs = graph_utm.graph['crs']
edges.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.7)
dest_utm.plot(ax=ax, color='blue', label='Destinations')
plt.axis('off')
list_axes_children_before = list(ax.get_children())

app_ui = ui.page_fluid(
  
        ui.panel_main(ui.output_text("click_info"), 
                      ui.output_plot("plot1", click=True, height = "800px",width="100%")
                      )
    
)

def server(input: Inputs, output: Outputs, session: Session):
    def remove_diff_list(temp1, temp2): 
       return [item.remove() for item in temp2 if item not in temp1]
   
    origin_node_reactive = reactive.Value(None)  # Add a new reactive value to store the updated origin_node

    @output
    @render.plot()
    def plot1():
        origin_node = origin_node_reactive.get()
        if origin_node is None:
            origin_node = random.sample(list(nodes.index), 1)[0]

        remove_diff_list(list_axes_children_before, list(ax.get_children()))



        nodes.loc[[origin_node]].plot(ax=ax, color='red', label='Origin')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=False, shadow=False, ncol=2, fontsize=13)
        plt.xlabel("x (m)")
        plt.ylabel("y (m)")

        node_id, filtered_distances, filtered_paths = compute_distances_and_paths_from_single_node(origin_node, graph_utm, closest_target_nodes, weight='length')

        paths = [LineString(list(nodes.loc[filtered_paths[destination]].geometry.values)) for destination in filtered_paths]
        # Create GeoDataFrame from paths
        routes = gpd.GeoDataFrame(geometry=paths, crs=crs)

        # Set up a colormap to get unique colors
        cmap = plt.cm.get_cmap('viridis', len(routes))

        # Plot each route with a different color
        for idx, route in routes.iterrows():
            color = mcolors.to_hex(cmap(idx))
            temp_gdf = gpd.GeoDataFrame({'geometry': [route['geometry']]}, crs=crs)
            temp_gdf.plot(ax=ax, linewidth=3, alpha=0.8, color=color)

            # Annotate the distance
            dest_node = closest_target_nodes[idx]
            dest_lat, dest_lon = nodes.loc[dest_node].geometry.y, nodes.loc[dest_node].geometry.x
            distance = filtered_distances[dest_node]
            ax.annotate(
                f"{distance:.0f} m",
                xy=(dest_lon, dest_lat),
                xytext=(dest_lon - 0.001, dest_lat - 0.0015),
                fontsize=10,
                color="black"
            )

        return fig

    @output
    @render.text()
    def click_info():
        click_data = input.plot1_click()
        if click_data:
            x, y = click_data['x'], click_data['y']
            origin_node = ox.distance.nearest_nodes(graph_utm, X=[x], Y=[y])[0]
            origin_node_reactive.set(origin_node)  # Update the reactive value with the new origin_node

app = App(app_ui, server, debug=True)


