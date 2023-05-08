import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from shapely.geometry import LineString
import geopandas as gpd
import numpy as np

def plot_connected_points(src_points, closest_points, closest_distances, figsize=(6, 6)):
    
    destinations = closest_points.drop_duplicates()
    # Create a GeoDataFrame with LineStrings connecting src_points and closest_points
    connections = gpd.GeoDataFrame(
        geometry=[LineString([src, dst]) for src, dst in zip(src_points, closest_points)],
        data={'distance': closest_distances}
        #crs=src_points.crs,
    )
    
    fig, ax = plt.subplots(1, figsize=figsize)
    plt.title('Nearest Points Connections')

    # Plot the connecting links between points and color them based on distance
    segments = [np.array(line.coords)[:, :2] for line in connections.geometry]
    lc = LineCollection(segments, cmap='viridis', alpha=1, lw=1, zorder=1, label='Closest connection')
    lc.set_array(closest_distances)
    lc.set_clim(0, 8_000)  # Set color limits
    ax.add_collection(lc)
    
    # Add color bar
    cbar = plt.colorbar(lc, ax=ax)
    # Set colorbar label
    cbar.set_label('Distance (m)')

    # Plot the points
    src_points.plot(ax=ax, color='blue', markersize=2, alpha=0.5, zorder=2, label='People (sources)')
    destinations.plot(ax=ax, markersize=2, marker='o', color='red', alpha=1, zorder=3, label='Interest (destinations)')

    # Put a legend below the current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=False, shadow=False, ncol=2,fontsize = 13,frameon = False)
    plt.xlabel("lon (degrees)")
    plt.ylabel("lat (degrees)")
    
    plt.show()
    return fig,ax
