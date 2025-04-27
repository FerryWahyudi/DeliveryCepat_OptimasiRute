import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.patheffects as path_effects  

from algorithm.dijkstra import dijkstra, dijkstra_waktu
from algorithm.astar import astar, astar_waktu

# Warna default untuk rute kendaraan
colors = ['red', 'blue', 'green', 'purple', 'orange']

def visualize_manual(G, assignments, selected_algorithm, nodes_df, selected_vehicles):
    fig, ax = plt.subplots(figsize=(16, 10))

    pos = nx.kamada_kawai_layout(G)

    # Mapping Node ID ke Nama Lokasi
    node_labels = {
        row['Node ID']: (
            "Gudang Utama" if row['Node ID'] == "N01" 
            else row['Nama Lokasi'].replace(' ', '\n')
        )
        for _, row in nodes_df.iterrows()
}

    # Gambar semua node
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', edgecolors='black', node_size=700, ax=ax)

    # Gambar edges dengan mempertimbangkan one-way dan two-way
    for u, v, data in G.edges(data=True):
        arah = data.get('arah', '').lower()

        if arah == 'two-way':
            # Gambar dari u ke v
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v)],
                edge_color='black', width=2.0,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=15,
                style='solid',
                ax=ax
            )
            # Gambar dari v ke u (kebalikannya)
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(v, u)],
                edge_color='black', width=2.0,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=20,
                style='solid',
                ax=ax
            )
        else:
            # One-way normal
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v)],
                edge_color='gray', width=1.5,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=20,
                style='solid',
                ax=ax
            )

    # Gambar label node
    # nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9, font_weight='bold', ax=ax)
    # Gambar label node dengan font putih dan stroke hitam
    for node_id, (x, y) in pos.items():
        label = node_labels.get(node_id, '')
        text = ax.text(
            x, y, label,
            fontsize=10,
            fontweight='bold',
            color='white',   # warna teks putih
            ha='center',
            va='center'
        )
        text.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground='black'),  # Outline hitam
            path_effects.Normal()
        ])

    # Highlight rute kendaraan yang dipilih
    if assignments and selected_vehicles:
        for idx, (vehicle, shipment_list) in enumerate(assignments.items()):
            if vehicle not in selected_vehicles:
                continue  # Lewati kendaraan yang tidak dipilih

            for shipment in shipment_list:
                start = "N01"
                end = shipment['Lokasi Tujuan']

                # Pilih algoritma
                if selected_algorithm == "Dijkstra (Jarak Terpendek)":
                    path, _ = dijkstra(G, start, end)
                elif selected_algorithm == "A* (Jarak Terpendek)":
                    path, _ = astar(G, start, end)
                elif selected_algorithm == "Dijkstra (Waktu Terkoreksi)":
                    path, _ = dijkstra_waktu(G, start, end)
                else:
                    path, _ = astar_waktu(G, start, end)

                if path:
                    path_edges = list(zip(path[:-1], path[1:]))

                    # Gambar rute pengiriman
                    nx.draw_networkx_edges(
                        G, pos, edgelist=path_edges,
                        width=5,
                        edge_color=colors[idx % len(colors)],
                        arrows=True,
                        arrowstyle='-|>',
                        arrowsize=20,
                        ax=ax
                    )

                    # 🏷️ Tambahkan label nama kendaraan di tengah jalur
                    for (u, v) in path_edges:
                        x = (pos[u][0] + pos[v][0]) / 2
                        y = (pos[u][1] + pos[v][1]) / 2
                        ax.text(
                            x, y, vehicle,
                            fontsize=8,
                            fontweight='bold',
                            color=colors[idx % len(colors)],
                            ha='center',
                            va='center',
                            bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2')
                        )

    ax.set_title('Visualisasi Jaringan Pengiriman (Manual Graph)', fontsize=18, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()

    st.pyplot(fig)