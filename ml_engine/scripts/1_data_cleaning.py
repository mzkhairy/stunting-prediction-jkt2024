import pandas as pd
import re
import os

# --- KONFIGURASI FILE ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_location_name(name):
    """
    Membersihkan nama wilayah.
    Rules:
    1. 'KEC.', 'KEL.', 'KOTA ADM.', 'KAB. ADM.' -> Dihapus.
    2. 'KEP.' -> Diganti 'KEPULAUAN' (Khusus Kepulauan Seribu).
    3. Trim spasi & Uppercase.
    """
    if pd.isna(name):
        return ""
    
    name_str = str(name).upper()
    
    # Rule Spesifik: Ganti KEP. menjadi KEPULAUAN (biasanya untuk Kep. Seribu)
    # Kita pakai replace manual dulu sebelum regex remove prefix lain
    if 'KEP.' in name_str:
        name_str = name_str.replace('KEP.', 'KEPULAUAN')
    
    # Regex untuk menghapus prefix administrasi (Kecamatan, Kelurahan, Kota, Kab)
    # Perhatikan: Kita TIDAK menghapus 'KEPULAUAN' yang baru saja kita fix di atas.
    # Kita hanya menghapus KEC, KEL, KOTA ADM, KAB ADM.
    name_str = re.sub(r'\b(KEC\.|KECAMATAN|KEL\.|KELURAHAN|KOTA ADM\.|KAB\. ADM\.)\s*', '', name_str, flags=re.I)
    
    return name_str.strip()

def process_kecamatan():
    print("--- Memproses Data Kecamatan ---")
    input_path = os.path.join(RAW_DIR, 'data_kecamatan.xlsx')
    
    try:
        df = pd.read_excel(input_path)
        print(f"Data awal: {df.shape}")
    except FileNotFoundError:
        print(f"Error: File {input_path} tidak ditemukan.")
        return

    # Definisi Kolom
    index_cols = ['periode_data', 'wilayah', 'kecamatan']
    
    # Kolom statis (yang nilainya berulang di setiap baris kondisi_bayi)
    static_cols = [
        'jumlah_balita_kurus', 
        'jumlah_balita_kurus_mendapat_pmt', 
        'jumlah_balita_0_59_bulan_yang_ditimbang', 
        'jumlah_balita_berat_badan_kurang_bb_per_u', 
        'jumlah_balita_pendek', 
        'jumlah_bayi_lahir'
    ]
    
    existing_static_cols = [c for c in static_cols if c in df.columns]
    
    # --- LANGKAH A: PIVOT KONDISI BAYI ---
    pivot_df = df.pivot_table(
        index=index_cols, 
        columns='kondisi_bayi', 
        values='jumlah_kondisi_bayi',
        aggfunc='sum'
    )
    
    # --- LANGKAH B: AMBIL DATA STATIS ---
    static_df = df.groupby(index_cols)[existing_static_cols].first()
    
    # --- LANGKAH C: GABUNGKAN (MERGE) ---
    merged_df = pd.concat([static_df, pivot_df], axis=1).reset_index()
    merged_df.columns.name = None
    
    # --- LANGKAH D: CLEANING NAMA WILAYAH ---
    merged_df['kecamatan_clean'] = merged_df['kecamatan'].apply(clean_location_name)
    
    # --- LANGKAH E: FINAL AGGREGATION ---
    numeric_cols = existing_static_cols + list(pivot_df.columns)
    
    # Group by nama kecamatan yang sudah bersih
    final_df = merged_df.groupby(['periode_data', 'wilayah', 'kecamatan_clean'])[numeric_cols].sum().reset_index()
    final_df = final_df.fillna(0)
    
    # Rename kolom (lowercase & underscore)
    final_df.columns = [str(col).lower().replace(' ', '_').replace('(', '').replace(')', '') for col in final_df.columns]

    print(f"Data final kecamatan: {final_df.shape}")
    # Print contoh untuk memastikan Kepulauan Seribu benar
    print("Contoh Data (Cek Kepulauan):")
    print(final_df[final_df['kecamatan_clean'].str.contains('KEPULAUAN', na=False)].head(1))
    
    output_path = os.path.join(PROCESSED_DIR, 'clean_kecamatan.csv')
    final_df.to_csv(output_path, index=False)
    print(f"Disimpan ke: {output_path}\n")

def process_kelurahan():
    print("--- Memproses Data Kelurahan ---")
    input_path = os.path.join(RAW_DIR, 'data_kelurahan.xlsx')
    
    try:
        df = pd.read_excel(input_path)
    except FileNotFoundError:
        print(f"Error: File {input_path} tidak ditemukan.")
        return

    # Cleaning Nama Kelurahan
    df['kelurahan_clean'] = df['kelurahan'].apply(clean_location_name)
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'periode_data' in numeric_cols: numeric_cols.remove('periode_data')

    final_df = df.groupby(['periode_data', 'wilayah', 'kelurahan_clean'])[numeric_cols].sum().reset_index()
    final_df.columns = [str(col).lower().replace(' ', '_') for col in final_df.columns]
    
    output_path = os.path.join(PROCESSED_DIR, 'clean_kelurahan.csv')
    final_df.to_csv(output_path, index=False)
    print(f"Disimpan ke: {output_path}\n")

if __name__ == "__main__":
    process_kecamatan()
    process_kelurahan()