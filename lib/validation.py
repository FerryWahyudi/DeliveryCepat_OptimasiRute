import os
import pandas as pd
import streamlit as st
from app import build_graph
from algorithm.dijkstra import dijkstra_path

DATA_DIR = 'data'
nodes_path = os.path.join(DATA_DIR, 'nodes.csv')
edges_path = os.path.join(DATA_DIR, 'edges.csv')
shipments_path = os.path.join(DATA_DIR, 'shipments.csv')

def load_data():
    nodes_df = pd.read_csv(nodes_path, sep=';', encoding='utf-8')
    edges_df = pd.read_csv(edges_path, sep=';', encoding='utf-8')
    shipments_df = pd.read_csv(shipments_path, sep=';', encoding='latin1')
    return nodes_df, edges_df, shipments_df

nodes_df, edges_df, shipments_df = load_data()
G = build_graph(nodes_df, edges_df)

# ✅ Tambahkan UI untuk input
source = st.selectbox("Pilih node asal", nodes_df['Node ID'].tolist())
target = st.selectbox("Pilih node tujuan", nodes_df['Node ID'].tolist())

if st.button("Hitung Rute"):
    route = dijkstra_path(G, source, target)
    st.write("Route:", route)
    st.write("Type of route:", type(route))
