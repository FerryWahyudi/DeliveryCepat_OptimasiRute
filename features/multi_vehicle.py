def assign_shipments_to_vehicles(shipments, num_vehicles, max_capacity):
    """
    Membagi pengiriman ke beberapa kendaraan berdasarkan kapasitas kendaraan.
    """
    vehicles = {f'Vehicle_{i+1}': [] for i in range(num_vehicles)}
    vehicle_loads = [0] * num_vehicles  # Tracking berat per kendaraan

    for shipment in shipments:
        berat_barang = shipment.get('Berat (kg)', 0)

        # Cari kendaraan yang masih cukup kapasitasnya
        assigned = False
        for i in range(num_vehicles):
            if vehicle_loads[i] + berat_barang <= max_capacity:
                vehicles[f'Vehicle_{i+1}'].append(shipment)
                vehicle_loads[i] += berat_barang
                assigned = True
                break

        # Kalau semua kendaraan penuh, masuk ke kendaraan dengan muatan paling kecil
        if not assigned:
            min_load_idx = vehicle_loads.index(min(vehicle_loads))
            vehicles[f'Vehicle_{min_load_idx+1}'].append(shipment)
            vehicle_loads[min_load_idx] += berat_barang

    return vehicles

def calculate_vehicle_loads(assignments, vehicle_capacities):
    """
    Menghitung total berat dan persentase kapasitas terpakai untuk tiap kendaraan.
    """
    vehicle_loads = []
    for idx, (vehicle_id, shipments) in enumerate(assignments.items()):
        total_berat = sum(shipment.get('Berat (kg)', 0) for shipment in shipments)
        kapasitas = vehicle_capacities[idx] if idx < len(vehicle_capacities) else vehicle_capacities[-1]
        persentase = (total_berat / kapasitas) * 100 if kapasitas else 0

        vehicle_loads.append({
            'Vehicle': vehicle_id,
            'Total Berat (kg)': total_berat,
            'Kapasitas Maksimal (kg)': kapasitas,
            'Persentase Terpakai (%)': persentase
        })

    return vehicle_loads
