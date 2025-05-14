# Library Import
import streamlit as st
import pandas as pd
import networkx as nx
import osmnx as ox

# Modul visualisasi dan analisis
from visualzation.manual_garph import visualize_manual
from visualzation.osm_garph import visualize_osm
from analysis.analyze_algorithm import run_analysis_algorithm
from analysis.analyze_complexity import run_complexity_analysis
from analysis.analyze_comparative import run_comparative_analysis

# Modul algoritma dan fitur
from algorithm.dijkstra import dijkstra, dijkstra_waktu
from algorithm.astar import astar, astar_waktu
from features.multi_vehicle import assign_shipments_to_vehicles_prioritas_merata
from features.prioritized import prioritize_shipments
from features.multi_vehicle import calculate_vehicle_loads


# KONFIGURASI STREAMLIT
st.set_page_config(page_title="DeliveryCepat - Optimasi Rute Pengiriman", layout="wide")


# LOAD DATA
@st.cache_data
def load_data():
    nodes = pd.read_excel("data/dataset_rute.xlsx", sheet_name="Nodes")
    edges = pd.read_excel("data/dataset_rute.xlsx", sheet_name="Edges")
    shipments = pd.read_excel("data/dataset_rute.xlsx", sheet_name="Shipments")
    return nodes, edges, shipments

nodes_df, edges_df, shipments_df = load_data()


# CREATE GRAPH MANUAL
def create_graph(nodes_df, edges_df):
    G = nx.DiGraph()  # Directed Graph

    # Tambahkan semua node
    for _, row in nodes_df.iterrows():
        G.add_node(row['Node ID'], nama=row['Nama Lokasi'])

    # Tambahkan edge berdasarkan arah
    for _, row in edges_df.iterrows():
        dari = row['Dari']
        ke = row['Ke']
        arah = row['Arah']

        G.add_edge(
            dari, ke,
            length=row['Panjang (km)'],
            kecepatan=row['Kecepatan Rata-rata (km/jam)'],
            arah=arah,
            kondisi=row['Kondisi Jalan'],
            kemacetan=row['Kemacetan']
        )

        # Kalau Two-way, tambahkan juga dari Ke -> Dari
        if arah.lower() == 'two-way':
            G.add_edge(
                ke, dari,
                length=row['Panjang (km)'],
                kecepatan=row['Kecepatan Rata-rata (km/jam)'],
                arah=arah,
                kondisi=row['Kondisi Jalan'],
                kemacetan=row['Kemacetan']
            )

    return G

G = create_graph(nodes_df, edges_df)


# SIDEBAR SETTINGS
st.sidebar.header("Pengaturan")

with st.sidebar.expander("Algoritma & Kendaraan", expanded=False):
    selected_algorithm = st.selectbox(
        "Pilih Algoritma Optimasi",
        ("Dijkstra (Jarak Terpendek)", "A* (Jarak Terpendek)",
         "Dijkstra (Waktu Terkoreksi)", "A* (Waktu Terkoreksi)"),
        index=0
    )
    vehicle_count = st.slider("Jumlah Kendaraan", 1, 5, 3)
    vehicle_capacity = st.slider("Kapasitas Kendaraan (kg)", 50, 200, 70)
    use_priority = st.checkbox("Gunakan Prioritas Pengiriman", value=False)

with st.sidebar.expander("Tampilan Peta", expanded=False):
    use_osm = st.checkbox("Gunakan Peta OpenStreetMap", value=False)
    if use_osm:
        map_style = st.selectbox(
            "Style Peta",
            ["OpenStreetMap", "CartoDB Positron", "Stamen Terrain"],
            index=0
        )

with st.sidebar.expander("Pengaturan Lanjutan", expanded=False):
    analyze_algorithm = st.checkbox("Analisis Algoritma Pada Pengiriman", value=False)
    analyze_complexity = st.checkbox("Analisis Kompleksitas Waktu dan Ruang", value=False)
    analyze_comparative = st.checkbox("Analisis Komparatif Algoritma", value=False)

# Kapasitas kendaraan
vehicle_capacities = [vehicle_capacity] * vehicle_count


# PERSIAPAN DATA PENGIRIMAN
shipments = shipments_df.copy()

if use_priority:
    shipments = prioritize_shipments(shipments)

assignments = assign_shipments_to_vehicles_prioritas_merata(shipments.to_dict('records'), vehicle_count, vehicle_capacity)

selected_vehicles = st.sidebar.multiselect(
    "Pilih Kendaraan untuk Ditampilkan",
    options=list(assignments.keys()),
    default=list(assignments.keys())
)


# MAIN TITLE
st.title("🚛 Visualisasi Optimasi Rute Pengiriman")


# VISUALISASI RUTE
if use_osm:
    avg_lat = nodes_df['Latitude'].mean()
    avg_lon = nodes_df['Longitude'].mean()

    try:
        # Load OSM
        G_osm = ox.graph_from_place('Palangka Raya, Indonesia', network_type='drive')
        if len(G_osm.nodes) > 0:
            visualize_osm(G_osm, assignments, selected_algorithm, nodes_df)
        else:
            st.warning("🔄 Peta OSM kosong, beralih ke peta manual.")
            visualize_manual(G, assignments, selected_algorithm, nodes_df, selected_vehicles)
    except:
        st.warning("🔄 Gagal load peta OSM, beralih ke peta manual.")
        visualize_manual(G, assignments, selected_algorithm, nodes_df, selected_vehicles)

else:
    visualize_manual(G, assignments, selected_algorithm, nodes_df, selected_vehicles)


# RINGKASAN MUATAN
vehicle_summary = calculate_vehicle_loads(assignments, vehicle_capacities)
summary_df = pd.DataFrame(vehicle_summary)
st.subheader("🚚 Ringkasan Muatan Kendaraan")
st.dataframe(summary_df)


# RUTE PENGIRIMAN
st.subheader("📦 Rute Tujuan Utama Pengiriman")

nama_lokasi = dict(zip(nodes_df['Node ID'], nodes_df['Nama Lokasi']))

for idx, (vehicle, shipment_list) in enumerate(assignments.items()):
    if not shipment_list:
        continue

    # Rute pengiriman hanya berdasarkan lokasi tujuan
    rute = ["Gudang Utama"]
    for shipment in shipment_list:
        tujuan = shipment['Lokasi Tujuan']
        nama_tujuan = nama_lokasi.get(tujuan, tujuan)
        rute.append(nama_tujuan)

    rute_str = " → ".join(rute)
    st.markdown(f"**Kendaraan {idx+1}:** {rute_str}")


# DETAIL PENGIRIMAN
st.subheader("📦 Detail Pengiriman per Kendaraan")

for idx, (vehicle, shipment_list) in enumerate(assignments.items()):
    if not shipment_list:
        continue

    with st.expander(f"🚛 Kendaraan {idx+1}", expanded=False):
        rute_info = []
        full_route = []  # <- Menampung semua node yang dilalui
        total_jarak = 0
        total_waktu = 0
        total_biaya = 0
        current_node = "N01"

        for shipment in shipment_list:
            tujuan = shipment['Lokasi Tujuan']

            # Pilih algoritma
            if selected_algorithm == "Dijkstra (Jarak Terpendek)":
                path, cost = dijkstra(G, current_node, tujuan)
            elif selected_algorithm == "A* (Jarak Terpendek)":
                path, cost = astar(G, current_node, tujuan)
            elif selected_algorithm == "Dijkstra (Waktu Terkoreksi)":
                path, cost = dijkstra_waktu(G, current_node, tujuan)
            else:
                path, cost = astar_waktu(G, current_node, tujuan)

            if path:
                jarak = cost["jarak"]
                waktu = cost["waktu"]
                biaya = cost.get("biaya", 0)

                total_jarak += jarak
                total_waktu += waktu
                total_biaya += biaya

                # Tambahkan semua node ke full_route
                if not full_route:
                    full_route.extend(path)
                else:
                    # Hindari duplikat node yang sama di ujung
                    full_route.extend(path[1:])

                # Tambahkan detail per edge
                for i in range(len(path) - 1):
                    u = path[i]
                    v = path[i+1]

                    data_edge = G.get_edge_data(u, v)

                    if data_edge:
                        nama_awal = nama_lokasi.get(u, u)
                        nama_tujuan = nama_lokasi.get(v, v)
                        jarak_edge = data_edge.get('length', 0)
                        kecepatan_edge = data_edge.get('kecepatan', 1)
                        arah_edge = data_edge.get('arah', 'One-way')
                        kondisi_edge = data_edge.get('kondisi', '-')
                        kemacetan_edge = data_edge.get('kemacetan', '-')

                        waktu_edge = (jarak_edge / kecepatan_edge) * 60  # konversi jam ke menit

                        rute_info.append({
                            'Dari': nama_awal,
                            'Ke': nama_tujuan,
                            'Jarak (km)': f"{jarak_edge:.2f}",
                            'Waktu Tempuh': f"{waktu_edge:.1f} menit" if waktu_edge < 60 else f"{waktu_edge/60:.2f} jam",
                            'Arah': arah_edge,
                            'Kondisi Jalan': kondisi_edge,
                            'Kemacetan': kemacetan_edge,
                            'Prioritas': shipment.get('Prioritas', 'Normal')
                        })

                current_node = tujuan

        if rute_info:
            # Build rute lengkap dari full_route
            rute_str = " → ".join([nama_lokasi.get(node, node) for node in full_route])
            st.markdown(f"**Rute Lengkap:** {rute_str}")

            st.markdown("**Detail Perjalanan:**")
            detail_df = pd.DataFrame(rute_info)
            st.dataframe(detail_df, use_container_width=True)

            st.markdown(f"""
            **Total Jarak:** {total_jarak:.2f} km  
            **Total Waktu:** {total_waktu:.1f} menit ({total_waktu/60:.2f} jam)  
            **Total Biaya:** Rp {int(total_biaya):,}
            """)
        else:
            st.warning("Tidak ada rute ditemukan untuk kendaraan ini.")



# ANALISIS OPSIONAL
if analyze_algorithm:
    st.subheader("🔎 Analisis Algoritma")
    algorithms = {
        "Dijkstra (Jarak Terpendek)": lambda G, start, end: dijkstra(G, start, end),
        "A* (Jarak Terpendek)": lambda G, start, end: astar(G, start, end),
        "Dijkstra (Waktu Terkoreksi)": lambda G, start, end: dijkstra_waktu(G, start, end),
        "A* (Waktu Terkoreksi)": lambda G, start, end: astar_waktu(G, start, end)
    }
    analysis_result = run_analysis_algorithm(algorithms, G, assignments, selected_algorithm)
    result_df = pd.DataFrame(analysis_result)
    st.dataframe(result_df)

if analyze_complexity:
    st.subheader("🧠 Analisis Kompleksitas Waktu & Memori")
    run_complexity_analysis(G, assignments)

if analyze_comparative:
    st.subheader("⚡ Analisis Komparatif Algoritma")
    run_comparative_analysis(G, assignments)
