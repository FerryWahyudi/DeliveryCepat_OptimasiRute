import time
import tracemalloc
import streamlit as st
import pandas as pd
import networkx as nx
from algorithm.dijkstra import dijkstra, dijkstra_waktu
from algorithm.astar import astar, astar_waktu

def run_comparative_analysis(G, assignments):
    """
    Analisis komparatif algoritma berdasarkan:
    - Waktu komputasi
    - Memori digunakan
    - Total jarak, waktu, biaya
    - Jumlah node dan edge
    """

    algorithms = {
        "Dijkstra (Jarak Terpendek)": dijkstra,
        "Dijkstra (Waktu Terkoreksi)": dijkstra_waktu,
        "A* (Jarak Terpendek)": astar,
        "A* (Waktu Terkoreksi)": astar_waktu
    }

    results = {
        "Algoritma": [],
        "Waktu Komputasi (detik)": [],
        "Memori Digunakan (KB)": [],
        "Total Jarak": [],
        "Total Waktu": [],
        "Total Biaya": [],
        "Jumlah Node": [],
        "Jumlah Edge": []
    }

    for algo_name, algo_func in algorithms.items():
        total_distance = 0
        total_time_travel = 0
        total_cost = 0
        used_nodes = set()
        used_edges = set()

        start_time = time.time()
        tracemalloc.start()

        for vehicle, shipment_list in assignments.items():
            current_node = "N01"

            for shipment in shipment_list:
                tujuan = shipment["Lokasi Tujuan"]
                path, cost = algo_func(G, current_node, tujuan)

                if path and len(path) > 1:
                    total_distance += cost.get("jarak", 0)
                    total_time_travel += cost.get("waktu", 0)
                    total_cost += cost.get("biaya", 0)

                    for i in range(len(path) - 1):
                        node1 = path[i]
                        node2 = path[i+1]
                        used_edges.add((node1, node2))

                        used_nodes.add(node1)
                        used_nodes.add(node2)

                current_node = tujuan

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        exec_time = time.time() - start_time

        results["Algoritma"].append(algo_name)
        results["Waktu Komputasi (detik)"].append(round(exec_time, 5))
        results["Memori Digunakan (KB)"].append(round(peak / 1024, 2))
        results["Total Jarak"].append(round(total_distance, 2))
        results["Total Waktu"].append(round(total_time_travel, 2))
        results["Total Biaya"].append(round(total_cost, 2))
        results["Jumlah Node"].append(len(used_nodes))
        results["Jumlah Edge"].append(len(used_edges))

    # Tampilkan hasil
    st.subheader("📈 Hasil Analisis Komparatif Algoritma")
    results_df = pd.DataFrame(results)
    st.dataframe(results_df)

    # Optional: visualisasi
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 7))
        for metric in ["Waktu Komputasi (detik)", "Memori Digunakan (KB)", "Total Jarak", "Total Waktu", "Total Biaya"]:
            ax.plot(results_df["Algoritma"], results_df[metric], marker='o', label=metric)

        ax.set_xlabel("Algoritma")
        ax.set_ylabel("Nilai")
        ax.set_title("Perbandingan Kinerja Algoritma")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)

    except Exception as e:
        st.warning(f"Gagal memuat plot: {e}")
