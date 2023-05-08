import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def distance_stats(closest_distances):
    stats = {
        'min': np.min(closest_distances),
        'max': np.max(closest_distances),
        'mean': np.mean(closest_distances),
        'median': np.median(closest_distances),
        'std': np.std(closest_distances),
    }
    return stats

def plot_distance_stats(closest_distances, bins=10, figsize=(10, 5)):
    stats = distance_stats(closest_distances)
    
    fig, ax = plt.subplots(1, figsize=figsize)
    plt.title('Distance Statistics')

    # Plot histogram of distances
    ax.hist(closest_distances, bins=bins, alpha=0.8, color='blue')
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Frequency')

    # Display the basic statistics on the plot
    stat_text = "\n".join([f"{key.capitalize()}: {value:.2f}" for key, value in stats.items()])
    ax.text(0.95, 0.95, stat_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.5))

    plt.show()
    

def plot_distance_comparison(distances1, distances2, labels=['Method 1', 'Method 2'], title='Distance Comparison'):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(distances1, kde=True, color='blue', label=labels[0], ax=ax)
    sns.histplot(distances2, kde=True, color='green', label=labels[1], ax=ax)
    ax.set(xlabel='Distance (m)', ylabel='Frequency', title=title)
    plt.legend()
    plt.show()
    



def plot_coordinate_comparison(closest_points, path_destinations):
    closest_x = [point.x for point in closest_points]
    closest_y = [point.y for point in closest_points]
    path_x = [point.x for point in path_destinations]
    path_y = [point.y for point in path_destinations]

    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.scatter(closest_x, closest_y, c='blue', label='Straight Lines', alpha=0.5)
    ax.scatter(path_x, path_y, c='green', label='Shortest Path', alpha=0.5)

    ax.set(xlabel='Longitude', ylabel='Latitude', title='Coordinate Comparison: Straight Lines vs. Shortest Path')
    plt.legend()
    plt.show()
