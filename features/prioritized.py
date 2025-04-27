import pandas as pd

def prioritize_shipments(shipments_df):
    """
    Mengurutkan shipments berdasarkan prioritas ('Tinggi', 'Sedang', 'Rendah') 
    dan batas waktu terkecil. 
    Prioritas lebih tinggi dan deadline lebih kecil diutamakan.
    """
    if 'Prioritas' not in shipments_df.columns or 'Batas Waktu (jam)' not in shipments_df.columns:
        # Kalau kolom tidak lengkap, return original
        return shipments_df

    # Mapping prioritas: semakin kecil nilai mapping, semakin tinggi prioritas
    priority_mapping = {
        'Tinggi': 1,
        'Sedang': 2,
        'Rendah': 3
    }

    # Buat kolom bantu untuk sorting
    shipments_df['Prioritas_Nilai'] = shipments_df['Prioritas'].map(priority_mapping)

    # Sortir: Prioritas dulu, baru Batas Waktu (semakin kecil semakin didahulukan)
    shipments_df_sorted = shipments_df.sort_values(
        by=['Prioritas_Nilai', 'Batas Waktu (jam)'],
        ascending=[True, True]
    ).reset_index(drop=True)

    # Drop kolom bantu setelah sorting
    shipments_df_sorted = shipments_df_sorted.drop(columns=['Prioritas_Nilai'])

    return shipments_df_sorted
