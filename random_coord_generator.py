import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt


def generate_random_points(x_min = -1.56, y_min = 52.86, x_max = -1.39, y_max =  52.96, n =100):
    np.random.seed(100)
    x = np.random.uniform(x_min, x_max, n)
    y = np.random.uniform(y_min, y_max, n)
    return gpd.GeoSeries(gpd.points_from_xy(x, y),crs = 'EPSG:4326')

def plot_source_destination_points(source_points, destination_points):
    # plot the points
    fig, ax = plt.subplots(1,figsize = (6,6))
    plt.title('Random points in Derby')
    source_points.plot(color='blue',ax=ax, label='People (sources)',markersize=10,    marker= "x")
    destination_points.plot(color='red', ax=ax, label='Interest (destinations)',markersize=10, marker = "o")
    plt.xlabel("lon (degrees)")
    plt.ylabel("lat (degrees)")
    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
              fancybox=False, shadow=False, ncol=5,fontsize = 13)
    
    plt.show()
    return fig,ax
