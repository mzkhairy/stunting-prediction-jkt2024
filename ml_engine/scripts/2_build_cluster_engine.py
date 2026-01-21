import pandas as pd
import numpy as np
import os
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- KONFIGURASI PATH ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
MODEL_DIR = os.path.join(BASE_DIR, 'ml_engine', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def safe_division(numerator, denominator):
    return np.where(denominator > 0, numerator / denominator, 0)

def load_data():
    """Load data hasil cleaning."""
    print("--- 1. Loading Processed Data ---")
    path_kec = os.path.join(PROCESSED_DIR, 'clean_kecamatan.csv')
    path_kel = os.path.join(PROCESSED_DIR, 'clean_kelurahan.csv')
    
    if not os.path.exists(path_kec) or not os.path.exists(path_kel):
        raise FileNotFoundError("Data CSV tidak ditemukan. Jalankan 1_data_cleaning.py dulu.")
    
    df_kec = pd.read_csv(path_kec)
    df_kel = pd.read_csv(path_kel)
    print(f"Data Loaded: {len(df_kec)} Kecamatan, {len(df_kel)} Kelurahan.")
    return df_kec, df_kel

def engineer_kecamatan(df):
    """
    Mengubah angka absolut menjadi RASIO (6 Faktor Utama).
    Ini adalah 'Feature Engineering' inti dari strategi kita.
    """
    print("\n--- 2. Computing Kecamatan Ratios (The 6 Factors) ---")
    
    # 1. Stunting (Existing Risk)
    df['rate_stunting'] = safe_division(df['jumlah_balita_pendek'], df['jumlah_balita_0_59_bulan_yang_ditimbang'])
    
    # 2. BBLR (Prenatal Risk)
    df['rate_bblr'] = safe_division(df['berat_bayi_lahir_rendah_bblr'], df['jumlah_bayi_lahir'])
    
    # 3. Lahir Mati (Maternal Risk)
    df['rate_lahir_mati'] = safe_division(df['bayi_lahir_mati'], df['jumlah_bayi_lahir'])
    
    # 4. Wasting (Acute Risk)
    df['rate_wasting'] = safe_division(df['jumlah_balita_kurus'], df['jumlah_balita_0_59_bulan_yang_ditimbang'])
    
    # 5. Gizi Kurang (Chronic Risk)
    total_gizi_masalah = df['balita_gizi_kurang'] + df['jumlah_balita_berat_badan_kurang_bb_per_u']
    df['rate_gizi_kurang'] = safe_division(total_gizi_masalah, df['jumlah_balita_0_59_bulan_yang_ditimbang'])
    
    # 6. PMT Coverage (Mitigation Factor)
    df['rate_pmt'] = safe_division(df['jumlah_balita_kurus_mendapat_pmt'], df['jumlah_balita_kurus'])
    
    # Isi NaN dengan 0
    df = df.fillna(0)
    
    return df

def cluster_kecamatan(df, n_clusters=3):
    """
    Melakukan K-Means untuk mencari pola 'Karakter Wilayah'.
    """
    print(f"\n--- 3. Clustering Kecamatan (k={n_clusters}) ---")
    
    features = ['rate_stunting', 'rate_bblr', 'rate_lahir_mati', 
                'rate_wasting', 'rate_gizi_kurang', 'rate_pmt']
    
    # Standardisasi agar BBLR (angka kecil) dianggap setara Stunting (angka besar)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    
    # K-Means Process
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster_id'] = kmeans.fit_predict(X_scaled)
    
    # Labeling Strategy:
    # Urutkan Cluster ID berdasarkan rata-rata Stunting agar konsisten
    # 0 = Paling Aman, 2 = Paling Bahaya
    avg_stunting = df.groupby('cluster_id')['rate_stunting'].mean().sort_values()
    mapping = {old_id: new_label for new_label, old_id in enumerate(avg_stunting.index)}
    
    df['risk_level'] = df['cluster_id'].map(mapping) # 0, 1, 2
    
    print("Cluster Risk Mapping (based on Stunting Rate):", mapping)
    print(df.groupby('risk_level')[features].mean())
    
    return df, features

def score_kelurahan(df):
    """
    Menilai Kelurahan berdasarkan Quantile (Peringkat).
    Karena datanya cuma 1 dimensi (jumlah kasus), kita pakai Ranking Statistika, bukan ML.
    """
    print("\n--- 4. Scoring Kelurahan (Quantile Ranking) ---")
    
    target = 'jumlah_balita_pendek'
    
    # Tentukan ambang batas (Threshold) berdasarkan data Jakarta
    q1 = df[target].quantile(0.25) # Batas Bawah (Zona Hijau)
    q3 = df[target].quantile(0.75) # Batas Atas (Zona Merah)
    
    def get_score(val):
        if val > q3: return 2 # High Risk
        elif val > q1: return 1 # Medium Risk
        return 0 # Low Risk
        
    df['risk_level'] = df[target].apply(get_score)
    
    print(f"Thresholds -> Hijau: <{int(q1)}, Kuning: {int(q1)}-{int(q3)}, Merah: >{int(q3)}")
    return df

def build_knowledge_base(df_kec, df_kel, kec_feats):
    """
    Menyusun 'Otak' yang akan dipakai Backend.
    Hanya berisi DATA, tidak ada teks narasi.
    """
    print("\n--- 5. Building Knowledge Base (Pure Data) ---")
    
    kb = {
        "meta": {
            "version": "v1.0-clustering",
            "thresholds": {
                "stunting_avg": df_kec['rate_stunting'].mean(),
                "bblr_avg": df_kec['rate_bblr'].mean(),
                "pmt_avg": df_kec['rate_pmt'].mean()
            }
        },
        "kecamatan": {},
        "kelurahan": {}
    }
    
    # A. Populate Kecamatan
    for _, row in df_kec.iterrows():
        # Simpan Statistik Mentah (untuk Backend logic)
        stats = {feat: round(row[feat], 4) for feat in kec_feats}
        
        kb["kecamatan"][row['kecamatan_clean']] = {
            "cluster_id": int(row['risk_level']), # Kita simpan risk level sbg ID utama
            "stats": stats
        }
        
    # B. Populate Kelurahan
    for _, row in df_kel.iterrows():
        kb["kelurahan"][row['kelurahan_clean']] = {
            "risk_level": int(row['risk_level']), # 0, 1, 2
            "case_count": int(row['jumlah_balita_pendek'])
        }
        
    # Save
    output_path = os.path.join(MODEL_DIR, 'regional_map.joblib')
    joblib.dump(kb, output_path)
    
    print(f"Knowledge Base saved to: {output_path}")
    print("DONE. Ready for Backend Integration.")

if __name__ == "__main__":
    # 1. Load
    df_kec_raw, df_kel_raw = load_data()
    
    # 2. Process
    df_kec_proc = engineer_kecamatan(df_kec_raw)
    df_kec_final, k_feats = cluster_kecamatan(df_kec_proc)
    df_kel_final = score_kelurahan(df_kel_raw)
    
    # 3. Save
    build_knowledge_base(df_kec_final, df_kel_final, k_feats)