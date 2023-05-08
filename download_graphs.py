import osmnx as ox


def download_place(place_name):
     graph = ox.graph_from_place(place_name, network_type="walk", simplify=True)
     filename = f"data/graph_{place_name.strip().replace(',', '').replace(' ', '_')}"
     ox.save_graph_geopackage(graph,f"{filename}.gpkg")
     ox.save_graphml(graph,f"{filename}.graphml")

list_places = ["Derby,England","London,England"]
for place in list_places:
    download_place(place)