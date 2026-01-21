import os
import joblib
import numpy as np

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_engine', 'models', 'regional_map.joblib')

try:
    KNOWLEDGE_BASE = joblib.load(MODEL_PATH)
except FileNotFoundError:
    KNOWLEDGE_BASE = None

# --- LOGIKA WHO & SPECTRUM (TETAP SAMA) ---

def calculate_who_spectrum(age_months, height, gender):
    """
    Menghitung Z-Score dan Posisi Spectrum.
    """
    if gender == 1:
        median = 49.9 + (age_months * 0.7) - (0.002 * age_months**2)
        sd = 1.9 + (age_months * 0.05)
    else:
        median = 49.1 + (age_months * 0.68) - (0.002 * age_months**2)
        sd = 1.8 + (age_months * 0.05)
        
    z_score = (height - median) / sd
    
    if z_score < -3:
        code, label, color = "severely_stunting", "Sangat Pendek", "#ef4444"
    elif z_score < -2:
        code, label, color = "stunting", "Pendek (Stunting)", "#f59e0b"
    else:
        code, label, color = "normal", "Normal", "#22c55e"
        
    min_visual, max_visual = -4.0, 2.0
    clamped_z = max(min_visual, min(z_score, max_visual))
    spectrum_pct = ((clamped_z - min_visual) / (max_visual - min_visual)) * 100
    
    if z_score > -1: hint = "Tumbuh Kembang Ideal"
    elif z_score > -1.9: hint = "Normal (Sedikit di bawah rata-rata)"
    elif z_score > -2.0: hint = "Normal (Hati-hati, Kritis!)"
    elif z_score > -2.5: hint = "Stunting Ringan"
    elif z_score > -3.0: hint = "Stunting Berat"
    else: hint = "Sangat Pendek (Perlu Penanganan Medis)"

    return {
        "status_code": code,
        "status_label": label,
        "z_score": round(z_score, 2),
        "spectrum_value": round(spectrum_pct, 1),
        "spectrum_color": color,
        "spectrum_hint": hint
    }

# --- LOGIKA REGIONAL INSIGHT (UPDATED NATURAL LANGUAGE) ---

def analyze_region(kecamatan_name, kelurahan_name):
    if not KNOWLEDGE_BASE:
        return default_insight()
        
    # 1. Normalisasi Nama
    kec_clean = kecamatan_name.upper().replace('KEC.', '').strip()
    if 'KEP.' in kec_clean and 'KEPULAUAN' not in kec_clean:
         kec_clean = kec_clean.replace('KEP.', 'KEPULAUAN')
    kel_clean = kelurahan_name.upper().replace('KEL.', '').strip()
    
    kec_data = KNOWLEDGE_BASE['kecamatan'].get(kec_clean)
    if not kec_data:
        return default_insight(f"Data Kecamatan '{kec_clean}' tidak ditemukan.")
        
    risk_code = kec_data['cluster_id']
    stats = kec_data['stats']
    thresholds = KNOWLEDGE_BASE['meta']['thresholds']
    
    scorecard = []
    explanations = [] 
    
    # --- HELPER: Evaluasi Fitur ---
    def evaluate_feature(label, value, threshold, is_reverse=False, explanation_template=""):
        if threshold == 0: threshold = 0.001
        diff_pct = ((value - threshold) / threshold) * 100
        avg_display = f"{round(threshold * 100, 1)}%"
        val_display = f"{round(value * 100, 1)}%"
        
        if abs(diff_pct) < 15:
            status = "neutral"
            text = f"Normal, setara rata-rata Jakarta ({avg_display})"
        elif (diff_pct > 0 and not is_reverse) or (diff_pct < 0 and is_reverse):
            status = "warning"
            comparison_text = "lebih rendah" if is_reverse else "lebih tinggi"
            text = f"Sedikit Berisiko, {comparison_text} dari rata-rata ({avg_display})"
            
            # REVISI: Ambang batas elaborasi diperketat. 
            # Jika beda > 20% (bukan 50%) sudah dianggap perlu action.
            if abs(diff_pct) > 20: 
                status = "bad"
                text = f"Tinggi, signifikan di atas rata-rata ({avg_display})" if not is_reverse else f"Rendah, signifikan di bawah rata-rata ({avg_display})"
                if explanation_template:
                    explanations.append(explanation_template)
        else:
            status = "good"
            comparison_text = "lebih tinggi" if is_reverse else "lebih rendah"
            text = f"Baik, {comparison_text} dari rata-rata ({avg_display})"
            
        return {
            "feature": label,
            "value_display": val_display,
            "status": status,
            "insight": text
        }

    # --- EVALUASI 6 FAKTOR ---
    res_stunting = evaluate_feature("Kasus Stunting", stats['rate_stunting'], thresholds['stunting_avg'])
    scorecard.append(res_stunting)
    
    scorecard.append(evaluate_feature("Berat Bayi Lahir Rendah", stats['rate_bblr'], thresholds['bblr_avg'], 
        explanation_template="pemantauan ketat ibu hamil (risiko BBLR tinggi)"))
    
    scorecard.append(evaluate_feature("Kesehatan Ibu Hamil", stats['rate_lahir_mati'], 0.01,
        explanation_template="peningkatan layanan vitalitas bayi baru lahir"))
    
    scorecard.append(evaluate_feature("Gizi Akut (Wasting)", stats['rate_wasting'], 0.05,
        explanation_template="intervensi pangan segera untuk balita kurus"))
    
    scorecard.append(evaluate_feature("Gizi Kronis", stats['rate_gizi_kurang'], 0.10,
        explanation_template="perbaikan sanitasi dan pola asuh jangka panjang"))
    
    # PMT
    pmt_val = stats['rate_pmt']
    avg_pmt = f"{round(thresholds['pmt_avg']*100, 1)}%"
    if pmt_val > 0.8:
        s_pmt, t_pmt = "good", f"Sangat Aktif ({avg_pmt})"
    elif pmt_val < 0.5:
        s_pmt, t_pmt = "bad", f"Kurang Optimal ({avg_pmt})"
        explanations.append("evaluasi distribusi PMT yang rendah")
    else:
        s_pmt, t_pmt = "neutral", f"Cukup ({avg_pmt})"
    scorecard.append({"feature": "Bantuan Gizi (PMT)", "value_display": f"{round(pmt_val*100, 1)}%", "status": s_pmt, "insight": t_pmt})

    # --- REVISI LOGIC KELURAHAN (MASUK KE ACTION PLAN) ---
    kel_data = KNOWLEDGE_BASE['kelurahan'].get(kel_clean)
    kel_narrative_part = ""
    
    if kel_data:
        k_risk = kel_data['risk_level']
        k_count = kel_data['case_count']
        
        if k_risk == 2: # MERAH
            status_text = f"TINGGI ({k_count} kasus)"
            kel_narrative_part = f"Secara spesifik, Kelurahan {kel_clean} berstatus ZONA MERAH MIKRO dengan intensitas kasus {status_text}."
            # FIX: Masukkan ke rekomendasi kebijakan!
            explanations.insert(0, f"intervensi lokus prioritas di Kelurahan {kel_clean} karena intensitas kasus sangat tinggi") 
            
        elif k_risk == 1: # KUNING
            status_text = f"WASPADA ({k_count} kasus)"
            kel_narrative_part = f"Di tingkat Kelurahan {kel_clean}, status tergolong {status_text}."
            explanations.append(f"peningkatan monitoring di Kelurahan {kel_clean}")
            
        else:
            kel_narrative_part = f"Kondisi Kelurahan {kel_clean} relatif aman ({k_count} kasus)."
    else:
        kel_narrative_part = "Data spesifik kelurahan belum tersedia."

    # --- SUSUN NARASI ---
    risk_labels = {0: "Zona Hijau", 1: "Zona Kuning", 2: "Zona Merah"}
    label_wilayah = risk_labels[risk_code]
    
    stunt_val = res_stunting['value_display']
    stunt_word = "terkendali" if res_stunting['status'] == 'good' else "perlu atensi"
    
    narrative_text = (
        f"Analisis Wilayah {label_wilayah}: Kecamatan {kec_clean} memiliki angka stunting {stunt_val} ({stunt_word}). "
        f"{kel_narrative_part}"
    )
    
    # Action Text Logic
    if explanations:
        action_text = "Rekomendasi Kebijakan Fokus pada: " + "; ".join(explanations) + "."
    else:
        action_text = "Rekomendasi Kebijakan: Pertahankan program monitoring rutin, tidak ditemukan indikator risiko mayor pada data wilayah ini."

    return {
        "risk_level": label_wilayah,
        "risk_code": risk_code,
        "scorecard": scorecard,
        "narrative": f"{narrative_text}\n\n{action_text}"
    }

def default_insight(msg="Data wilayah tidak ditemukan"):
    return {
        "risk_level": "Tidak Diketahui",
        "risk_code": -1,
        "scorecard": [],
        "narrative": msg
    }

def generate_recommendation(who_code, region_risk_code):
    if who_code in ['stunting', 'severely_stunting']:
        return "PRIORITAS MEDIS: Segera konsultasi ke dokter anak/Puskesmas. Pantau kurva pertumbuhan setiap bulan."
    
    if region_risk_code == 2:
        return "PENCEGAHAN EKSTRA: Anak saat ini normal, tapi lingkungan berisiko tinggi. Pastikan asupan protein hewani (telur/ikan) cukup setiap hari."
    elif region_risk_code == 1:
        return "WASPADA: Pertahankan gizi baik. Perhatikan kebersihan lingkungan sekitar rumah."
    else:
        return "PERTAHANKAN: Lanjutkan pola asuh yang sudah baik ini."