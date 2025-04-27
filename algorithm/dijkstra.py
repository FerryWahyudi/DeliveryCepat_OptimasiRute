import networkx as nx
import heapq

def dijkstra(G, start, end):
    """
    Dijkstra berdasarkan jarak (length).
    Mengembalikan path dan {jarak, waktu, biaya}.
    """
    queue = [(0, 0, start, [])]  # (total_jarak, total_waktu, node, path)
    visited = set()
    
    while queue:
        jarak, waktu, node, path = heapq.heappop(queue)

        if node in visited:
            continue
        visited.add(node)

        path = path + [node]

        if node == end:
            tarif_per_km = 5000  # biaya 5000 per km
            biaya = jarak * tarif_per_km
            return path, {"jarak": jarak, "waktu": waktu, "biaya": biaya}
        
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                edge_data = G.edges[node, neighbor]
                panjang_km = edge_data.get('length', 1)  # default 1 km
                kecepatan = edge_data.get('kecepatan', 40)  # default 40 km/jam
                kemacetan = edge_data.get('kemacetan', 1)  # default tidak macet

                waktu_menit = (panjang_km / kecepatan) * 60  # menit
                waktu_menit *= kemacetan

                heapq.heappush(queue, (jarak + panjang_km, waktu + waktu_menit, neighbor, path))

    return None, {"jarak": float('inf'), "waktu": float('inf'), "biaya": float('inf')}

def dijkstra_waktu(G, start, end):
    """
    Dijkstra berdasarkan waktu tempuh.
    Mengembalikan path dan {jarak, waktu, biaya}.
    """
    queue = [(0, 0, start, [])]  # (total_waktu, total_jarak, node, path)
    visited = set()

    while queue:
        waktu, jarak, node, path = heapq.heappop(queue)

        if node in visited:
            continue
        visited.add(node)

        path = path + [node]

        if node == end:
            tarif_per_km = 5000
            biaya = jarak * tarif_per_km
            return path, {"jarak": jarak, "waktu": waktu, "biaya": biaya}
        
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                edge_data = G.edges[node, neighbor]
                panjang_km = edge_data.get('length', 1)
                kecepatan = edge_data.get('kecepatan', 40)
                kemacetan = edge_data.get('kemacetan', 1)

                waktu_menit = (panjang_km / kecepatan) * 60
                waktu_menit *= kemacetan

                heapq.heappush(queue, (waktu + waktu_menit, jarak + panjang_km, neighbor, path))

    return None, {"jarak": float('inf'), "waktu": float('inf'), "biaya": float('inf')}
