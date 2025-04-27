import time
import tracemalloc
import pandas as pd
from algorithm.dijkstra import dijkstra, dijkstra_waktu
from algorithm.astar import astar, astar_waktu

def load_data(filepath):
    """
    Membaca data dari file Excel.

    """
    xls = pd.ExcelFile(filepath)
    nodes_df = pd.read_excel(xls, 'Nodes')
    edges_df = pd.read_excel(xls, 'Edges')
    shipments_df = pd.read_excel(xls, 'Shipments') if 'Shipments' in xls.sheet_names else None

    return nodes_df, edges_df, shipments_df

def measure_vehicle_route(algorithm_func, graph, shipment_list, start_node="N01"):
    """
    Mengukur performa untuk satu kendaraan dengan beberapa shipment.
    """
    start_time = time.time()
    tracemalloc.start()

    full_path = []
    total_jarak = 0
    total_waktu = 0
    total_biaya = 0

    current_node = start_node

    for shipment in shipment_list:
        end_node = shipment['Lokasi Tujuan']
        path, cost = algorithm_func(graph, current_node, end_node)

        if full_path and path:
            full_path.extend(path[1:])  
        else:
            full_path.extend(path)

        if isinstance(cost, dict):
            total_jarak += cost.get('jarak', 0)
            total_waktu += cost.get('waktu', 0)
            total_biaya += cost.get('biaya', 0)
        else:
            total_jarak += cost  # fallback kalau cuma angka (jarak saja)

        current_node = end_node  # Update posisi sekarang ke tujuan baru

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    exec_time = time.time() - start_time

    return {
        "path": full_path,
        "total_jarak": total_jarak,
        "total_waktu": total_waktu,
        "total_biaya": total_biaya,
        "execution_time": exec_time,
        "memory_peak": peak / 1024  # dalam KB
    }

def run_analysis_algorithm(algorithms, graph, assignments, selected_algorithm):
    """
    Menjalankan analisis untuk semua kendaraan yang dipilih.
    """
    results = []

    # Pilih algoritma yang dipakai
    if selected_algorithm == "Dijkstra (Jarak Terpendek)":
        algo_func = dijkstra
    elif selected_algorithm == "A* (Jarak Terpendek)":
        algo_func = astar
    elif selected_algorithm == "Dijkstra (Waktu Terkoreksi)":
        algo_func = dijkstra_waktu
    else:  # Default
        algo_func = astar_waktu

    for vehicle, shipment_list in assignments.items():
        perf = measure_vehicle_route(algo_func, graph, shipment_list)
        jumlah_node = len(perf["path"])
        jumlah_edge = jumlah_node - 1 if jumlah_node > 0 else 0

        results.append({
            "Kendaraan": vehicle,
            "Waktu Komputasi (detik)": round(perf["execution_time"], 5),
            "Memori Digunakan (KB)": round(perf["memory_peak"], 2),
            "Total Jarak (km)": round(perf["total_jarak"], 2),
            "Total Waktu (menit)": round(perf["total_waktu"], 2),
            "Total Biaya (Rp)": round(perf["total_biaya"], 2),
            "Jumlah Node dalam Rute": jumlah_node,
            "Jumlah Edge dalam Rute": jumlah_edge
        })

    return results
