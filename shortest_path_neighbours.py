import geopandas as gpd
from shapely.geometry import LineString
import osmnx as ox
from nearest_point import get_nearest_point
import pandas as pd

def shortest_route_graph(G_proj, origin, destination, k_neighbors=5):
    nodes = ox.graph_to_gdfs(G_proj, edges=False)
    CRS = nodes.crs
    
    # Reproject all data
    origin_proj = origin.to_crs(crs=CRS)
    destination_proj = destination.to_crs(crs=CRS)

    # Initialize the routes GeoDataFrame with columns
    routes = gpd.GeoDataFrame(columns=['id', 'origin', 'destination', 'distance', 'geometry'], crs=CRS)

    # Iterate over origins
    for oidx, orig in origin_proj.iterrows():

        # Find closest node from the graph
        closest_origin_node = ox.distance.nearest_nodes(G=G_proj, X=orig.geometry.x, Y=orig.geometry.y)

        # Create a GeoDataFrame for the current origin
        current_origin_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(orig.geometry), crs=CRS)

        # Find the k closest destinations for the current origin
        closest_destinations = get_nearest_point(current_origin_gdf, destination_proj, k_neighbors=k_neighbors, target_crs=CRS)

        # Find the shortest path and its distance for each origin-destination pair
        shortest_path_info = min(
            (
                (ox.distance.shortest_path(G_proj, closest_origin_node, ox.distance.nearest_nodes(G_proj, X=target_geom.x, Y=target_geom.y), weight='length', cpus=-1), target_geom)
                for tidx, target_geom in closest_destinations.items()
                if closest_origin_node != ox.distance.nearest_nodes(G_proj, X=target_geom.x, Y=target_geom.y)
            ),
            key=lambda x: LineString(nodes.loc[x[0]].geometry.values).length,
            default=(None, None)
        )

        # Extract the shortest path and its corresponding destination geometry
        shortest_route, closest_target = shortest_path_info

        if shortest_route:
            #print(oidx)
            # Create a LineString out of the shortest route
            path = LineString(nodes.loc[shortest_route].geometry.values)

            # Calculate the Euclidean length of the path
            shortest_distance = path.length

            # Transform orig and closest_target CRS to origin.crs
            orig_transformed = gpd.GeoSeries(orig.geometry, crs=CRS).to_crs(origin.crs).iloc[0]
            target_geom_transformed = gpd.GeoSeries(closest_target, crs=CRS).to_crs(origin.crs).iloc[0]

            # Append the result to the GeoDataFrame
            new_route = gpd.GeoDataFrame({'id': [f'R{oidx+1}'], 'origin': [orig_transformed], 'destination': [target_geom_transformed], 'distance': [shortest_distance], 'geometry': [path]}, crs=nodes.crs)
            routes = pd.concat([routes, new_route], ignore_index=True)

    return routes, origin_proj, destination_proj




def shortest_path_v0(G_proj, origin, destination):    
    
    nodes = ox.graph_to_gdfs(G_proj, edges=False)
    CRS = nodes.crs
    
    # Reproject all data
    origin_proj = origin.to_crs(crs=CRS)
    destination_proj = destination.to_crs(crs=CRS)
    
    # Initialize routes of the shortest path
    routes = gpd.GeoDataFrame(columns=['id', 'geometry'])
    
    # Iterate over origins and destinations
    for oidx, orig in origin_proj.iterrows():
        # Find the closest node from the graph
        closest_origin_node = ox.distance.nearest_nodes(G=G_proj, X=orig.geometry.x, Y=orig.geometry.y)
        
        # Iterate over targets
        for tidx, target in destination_proj.iterrows():
            # Find the closest node from the graph
            closest_target_node = ox.distance.nearest_nodes(G_proj, X=target.geometry.x, Y=target.geometry.y)
            
            # Check if origin and target nodes are the same
            if closest_origin_node == closest_target_node:
                print("Same origin and destination node. Skipping ..")
                continue
            
            # Find the shortest path between the points
            route = ox.distance.shortest_path(G_proj, closest_origin_node, closest_target_node, weight='length', cpus=-1)
            
            # Extract the nodes of the route
            route_nodes = nodes.loc[route]
            
            # Create a LineString out of the route
            path = LineString(list(route_nodes.geometry.values))
            
            # Append the result into the GeoDataFrame
            route_id = f"O{oidx+1}_D{tidx+1}"
            routes = pd.concat([routes, gpd.GeoDataFrame({'id': [route_id], 'geometry': [path]})], ignore_index=True)
    
    # Set geometry
    routes = routes.set_geometry('geometry')
    
    # Set coordinate reference system
    routes.crs = nodes.crs
    
    return routes, origin_proj, destination_proj
