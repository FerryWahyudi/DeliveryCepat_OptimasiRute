import folium
import networkx as nx
import streamlit as st
from streamlit_folium import st_folium
import osmnx as ox

# Warna default untuk rute kendaraan
colors = ['red', 'blue', 'green', 'purple', 'orange']

def visualize_osm(G_osm, assignments, selected_algorithm, nodes_df):
    avg_lat = nodes_df['Latitude'].mean()
    avg_lon = nodes_df['Longitude'].mean()

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    node_coords = {row['Node ID']: (row['Latitude'], row['Longitude']) for idx, row in nodes_df.iterrows()}
    nama_lokasi = dict(zip(nodes_df['Node ID'], nodes_df['Nama Lokasi']))

    if "N01" in node_coords:
        gudang_coord = node_coords["N01"]
        folium.Marker(
            gudang_coord,
            popup="Gudang Utama",
            icon=folium.Icon(color='grey', icon='building', prefix='fa')
        ).add_to(m)

    for idx, (vehicle, shipment_list) in enumerate(assignments.items()):
        for shipment in shipment_list:
            start_id = "N01"
            end_id = shipment['Lokasi Tujuan']

            start_coord = node_coords[start_id]
            end_coord = node_coords[end_id]

            start_node = ox.distance.nearest_nodes(G_osm, X=start_coord[1], Y=start_coord[0])
            end_node = ox.distance.nearest_nodes(G_osm, X=end_coord[1], Y=end_coord[0])

            if selected_algorithm in ["Dijkstra (Jarak Terpendek)", "Dijkstra (Waktu Terkoreksi)"]:
                route = nx.shortest_path(G_osm, start_node, end_node, weight='length')
            else:
                route = nx.astar_path(G_osm, start_node, end_node, weight='length')

            route_coords = [(G_osm.nodes[n]['y'], G_osm.nodes[n]['x']) for n in route]

            folium.PolyLine(
                route_coords,
                color=colors[idx % len(colors)],
                weight=5,
                opacity=0.8,
                tooltip=f"{vehicle}"
            ).add_to(m)

            folium.Marker(
                route_coords[-1],
                popup=f"Tujuan: {nama_lokasi.get(end_id, end_id)}",
                icon=folium.Icon(color=colors[idx % len(colors)])
            ).add_to(m)

    st_data = st_folium(m, width=1200, height=700)
    return st_data
