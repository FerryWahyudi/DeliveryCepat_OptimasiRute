import heapq
import networkx as nx

def astar(graph, start, end, heuristic=lambda x, y: 1, tarif_per_km=5000):
    queue = [(0, 0, start, [], 0, 0)]  
    # (f_score, jarak, current_node, path, waktu, biaya)

    visited = set()

    while queue:
        (f, cost, node, path, waktu, biaya) = heapq.heappop(queue)

        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == end:
            return path, {
                "jarak": cost,
                "waktu": waktu,
                "biaya": biaya
            }

        for neighbor in graph.neighbors(node):  # <- PENTING: pakai .neighbors
            if neighbor not in visited:
                edge_data = graph[node][neighbor]

                weight = edge_data.get("weight", 1)     # Jarak antar node
                panjang_km = edge_data.get("length", weight)  # Panjang (default pakai weight)
                kecepatan = edge_data.get('kecepatan', 40)    # Km per jam
                kemacetan = edge_data.get('kemacetan', 1)     # Faktor kemacetan

                waktu_edge = (panjang_km / kecepatan) * 60 * kemacetan  # waktu menit
                biaya_edge = weight * tarif_per_km

                g_cost = cost + weight
                g_waktu = waktu + waktu_edge
                g_biaya = biaya + biaya_edge

                h = heuristic(neighbor, end)
                f_score = g_cost + h

                heapq.heappush(queue, (f_score, g_cost, neighbor, path, g_waktu, g_biaya))

    return [], {"jarak": float("inf"), "waktu": float("inf"), "biaya": float("inf")}


def waktu_heuristik(node1, node2, graph):
    try:
        # Estimasi jarak terpendek ke tujuan
        jarak = nx.shortest_path_length(graph, node1, node2, weight='length')
    except:
        jarak = 1  # fallback jika gagal

    kecepatan_rata2 = 40  # km/jam
    return (jarak / kecepatan_rata2) * 60  # dalam menit

def astar_waktu(graph, start, end, heuristic=None):
    if heuristic is None:
        heuristic = lambda x, y: waktu_heuristik(x, y, graph)

    tarif_per_km = 5000
    queue = [(0, 0, start, [], 0, 0)]  # (f_score, waktu, current_node, path, total_waktu, total_biaya)
    visited = set()

    while queue:
        (f, waktu, node, path, total_waktu, total_biaya) = heapq.heappop(queue)

        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == end:
            return path, {
                "jarak": sum(graph[path[i]][path[i+1]]['length'] for i in range(len(path)-1)),
                "waktu": total_waktu,
                "biaya": total_biaya
            }

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                edge_data = graph[node][neighbor]

                panjang_km = edge_data.get("length", 1)
                kecepatan = edge_data.get("kecepatan", 40)
                kemacetan = edge_data.get("kemacetan", 1)

                waktu_edge = (panjang_km / kecepatan) * 60 * kemacetan
                biaya_edge = panjang_km * tarif_per_km

                g_waktu = total_waktu + waktu_edge
                g_biaya = total_biaya + biaya_edge
                h = heuristic(neighbor, end)
                f_score = g_waktu + h

                heapq.heappush(queue, (f_score, g_waktu, neighbor, path, g_waktu, g_biaya))

    return [], {"jarak": float("inf"), "waktu": float("inf"), "biaya": float("inf")}
