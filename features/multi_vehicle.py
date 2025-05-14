def assign_shipments_to_vehicles_prioritas_merata(shipments, num_vehicles, max_capacity):
    """
    Membagi pengiriman ke beberapa kendaraan berdasarkan prioritas secara merata
    dan tetap memperhatikan kapasitas kendaraan.
    """
    # Inisialisasi kendaraan
    vehicles = {f'Vehicle_{i+1}': [] for i in range(num_vehicles)}
    vehicle_loads = [0] * num_vehicles  # Berat total per kendaraan

    # Kelompokkan shipment berdasarkan prioritas
    priority_levels = ['Tinggi', 'Sedang', 'Rendah']
    shipments_by_priority = {level: [] for level in priority_levels}

    for shipment in shipments:
        prioritas = shipment.get('Prioritas', 'Rendah')
        if prioritas not in shipments_by_priority:
            prioritas = 'Rendah'
        shipments_by_priority[prioritas].append(shipment)

    # Distribusi siklikal berdasarkan prioritas
    for level in priority_levels:
        idx = 0  # indeks kendaraan
        for shipment in shipments_by_priority[level]:
            berat_barang = shipment.get('Berat (kg)', 0)

            # Coba masukkan ke kendaraan yang cukup kapasitas
            attempts = 0
            assigned = False
            while attempts < num_vehicles:
                if vehicle_loads[idx] + berat_barang <= max_capacity:
                    vehicles[f'Vehicle_{idx+1}'].append(shipment)
                    vehicle_loads[idx] += berat_barang
                    assigned = True
                    break
                idx = (idx + 1) % num_vehicles
                attempts += 1

            # Jika semua kendaraan penuh, masukkan ke kendaraan dengan beban terkecil
            if not assigned:
                min_idx = vehicle_loads.index(min(vehicle_loads))
                vehicles[f'Vehicle_{min_idx+1}'].append(shipment)
                vehicle_loads[min_idx] += berat_barang

            idx = (idx + 1) % num_vehicles  # lanjut ke kendaraan berikutnya

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
