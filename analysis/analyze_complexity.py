# analysis/analyze_complexity.py

import time
import tracemalloc
import streamlit as st
import pandas as pd
from algorithm.dijkstra import dijkstra, dijkstra_waktu
from algorithm.astar import astar, astar_waktu

def run_complexity_analysis(G, assignments):
    """
    Analisis kompleksitas waktu, ruang, dan kualitas solusi berdasarkan jumlah node dan edge.
    """

    algorithms = {
        "Dijkstra (Jarak Terpendek)": dijkstra,
        "Dijkstra (Waktu Terkoreksi)": dijkstra_waktu,
        "A* (Jarak Terpendek)": astar,
        "A* (Waktu Terkoreksi)": astar_waktu
    }

    results = {
        "Algoritma": [],
        "Jumlah Node": [],
        "Jumlah Edge": [],
        "Waktu Komputasi (detik)": [],
        "Memori Puncak (KB)": [],
        "Total Jarak": [],
        "Total Waktu": [],
        "Total Biaya": []
    }

    for algo_name, algo_func in algorithms.items():
        for vehicle, shipment_list in assignments.items():
            current_node = "N01"
            total_nodes = 0
            total_edges = 0
            total_jarak = 0
            total_waktu = 0
            total_biaya = 0

            start_time = time.time()
            tracemalloc.start()

            for shipment in shipment_list:
                tujuan = shipment["Lokasi Tujuan"]
                path, path_cost = algo_func(G, current_node, tujuan)

                if path:
                    total_nodes += len(path)
                    total_edges += max(len(path) - 1, 0)

                    if isinstance(path_cost, dict):
                        # Kalau cost berupa dict, misal {'jarak': 10, 'waktu': 15, 'biaya': 1000}
                        total_jarak += path_cost.get('jarak', 0)
                        total_waktu += path_cost.get('waktu', 0)
                        total_biaya += path_cost.get('biaya', 0)
                    else:
                        # Kalau cost berupa angka biasa (misal jarak saja)
                        total_jarak += path_cost

                current_node = tujuan

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            exec_time = time.time() - start_time

            results["Algoritma"].append(algo_name)
            results["Jumlah Node"].append(total_nodes)
            results["Jumlah Edge"].append(total_edges)
            results["Waktu Komputasi (detik)"].append(round(exec_time, 5))
            results["Memori Puncak (KB)"].append(round(peak / 1024, 2))
            results["Total Jarak"].append(round(total_jarak, 2))
            results["Total Waktu"].append(round(total_waktu, 2))
            results["Total Biaya"].append(round(total_biaya, 2))

    # Tampilkan hasil
    st.subheader("📊 Hasil Analisis Kompleksitas")

    results_df = pd.DataFrame(results)
    st.dataframe(results_df)

    # Optional: visualisasi
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        for algo in results_df["Algoritma"].unique():
            subset = results_df[results_df["Algoritma"] == algo]
            ax.plot(subset["Jumlah Node"], subset["Waktu Komputasi (detik)"], marker='o', label=algo)
        
        st.caption("Jumlah Node dan Edge di sini adalah total yang diproses selama pencarian jalur, bukan hanya rute akhir.")    

        ax.set_xlabel("Jumlah Node")
        ax.set_ylabel("Waktu Komputasi (detik)")
        ax.set_title("Kompleksitas Waktu terhadap Jumlah Node")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.warning(f"Gagal memuat plot: {e}")
