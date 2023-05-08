import geopandas as gpd
from sklearn.neighbors import BallTree
import numpy as np

def get_nearest_point(src_points, dest_points, k_neighbors=1, source_crs='EPSG:4326', target_crs='EPSG:3857'):
    """Find nearest neighbors for all source points from a set of candidate points"""
    
    # Convert to GeoDataFrames with the source CRS
    src_gdf = gpd.GeoDataFrame(geometry=src_points, crs=source_crs)
    dest_points_gdf = gpd.GeoDataFrame(geometry=dest_points, crs=source_crs)
    
    # Project to the target CRS
    src_gdf = src_gdf.to_crs(target_crs)
    dest_points_gdf = dest_points_gdf.to_crs(target_crs)
    
    # get coordinates for BallTree
    src_coords = np.array([geom.coords[0] for geom in src_gdf.geometry])
    dest_points_coords = np.array([geom.coords[0] for geom in dest_points_gdf.geometry])

    # Create tree from the destination points
    tree = BallTree(dest_points_coords, leaf_size=15)

    # Find closest points and distances
    distances, indices = tree.query(src_coords, k=k_neighbors)

    # Transpose to get distances and indices into arrays
    distances = distances.transpose()
    indices = indices.transpose()

    # Get closest indices and distances (i.e. array at index 0)
    closest = indices[0]
    closest_dist = distances[0]

    # Convert points back to its original crs
    closest_points = [dest_points_gdf.geometry.iloc[idx] for idx in closest]
    closest_points = gpd.GeoSeries(closest_points, crs=target_crs).to_crs(source_crs)

    return (closest_points, closest_dist)
