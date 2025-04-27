import heapq

import heapq

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


def astar_waktu(graph, start, end, heuristic=lambda x, y: 1):
    tarif_per_km = 5000  # Biaya 5000 per km
    queue = [(0, 0, start, [], 0, 0)]  
    # (f_score, jarak, current_node, path, waktu, biaya)

    visited = set()

    while queue:
        (f, jarak, node, path, waktu, biaya) = heapq.heappop(queue)

        if node in visited:
            continue

        visited.add(node)
        path = path + [node]

        if node == end:
            return path, {
                "jarak": jarak,
                "waktu": waktu,
                "biaya": biaya
            }

        for neighbor in graph.neighbors(node):  # <-- DIUBAH .get jadi .neighbors
            if neighbor not in visited:
                edge_data = graph[node][neighbor]

                weight = edge_data.get("weight", 1)     # jarak antar node
                panjang_km = edge_data.get("length", 1)  # panjang dalam km
                kecepatan = edge_data.get('kecepatan', 40)  # km per jam
                kemacetan = edge_data.get('kemacetan', 1)  # faktor kemacetan

                waktu_edge = (panjang_km / kecepatan) * 60 * kemacetan  # waktu dalam menit
                biaya_edge = weight * tarif_per_km  # biaya untuk edge ini

                g_jarak = jarak + weight
                g_waktu = waktu + waktu_edge
                g_biaya = biaya + biaya_edge

                g = g_jarak  # Fokus pada jarak
                h = heuristic(neighbor, end)

                f_score = g + h

                heapq.heappush(queue, (f_score, g_jarak, neighbor, path, g_waktu, g_biaya))

    return [], {"jarak": float("inf"), "waktu": float("inf"), "biaya": float("inf")}