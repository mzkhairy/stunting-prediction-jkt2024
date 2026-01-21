# backend/app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ChildInput, PredictionResponse
from .services import calculate_who_spectrum, analyze_region, generate_recommendation
import joblib
import os

app = FastAPI(title="Stunting Prediction API", version="1.1.0")

# --- SETUP CORS (Agar Frontend bisa akses) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Di production, ganti dengan URL frontend spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SETUP PATH MODEL ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'ml_engine', 'models', 'regional_map.joblib')

@app.get("/")
def read_root():
    return {"message": "Stunting Prediction API is Running. Use POST /predict to analyze."}

@app.get("/locations")
def get_locations():
    """
    Endpoint KHUSUS untuk Frontend:
    Mengambil daftar Kecamatan & Kelurahan dari file model (.joblib)
    agar dropdown di UI terisi otomatis.
    """
    try:
        if not os.path.exists(MODEL_PATH):
             raise HTTPException(status_code=500, detail="Model file not found. Run clustering script first.")
             
        kb = joblib.load(MODEL_PATH)
        
        # Ambil keys dan urutkan abjad
        kecamatan_list = sorted(list(kb['kecamatan'].keys()))
        kelurahan_list = sorted(list(kb['kelurahan'].keys()))
        
        return {
            "kecamatan": kecamatan_list,
            "kelurahan": kelurahan_list
        }
    except Exception as e:
        print(f"Error loading locations: {e}")
        raise HTTPException(status_code=500, detail="Gagal memuat data wilayah")

@app.post("/predict", response_model=PredictionResponse)
def predict_stunting_risk(data: ChildInput):
    # 1. Analisis Fisik (Pakai Spectrum Calculator)
    who_res = calculate_who_spectrum(data.umur_bulan, data.tinggi_badan, data.jenis_kelamin)
    
    # 2. Analisis Wilayah (Pakai Simple Language Scorecard)
    regional_res = analyze_region(data.kecamatan, data.kelurahan)
    
    # 3. Rekomendasi
    final_rec = generate_recommendation(who_res['status_code'], regional_res['risk_code'])
    
    return {
        "child_analysis": who_res,
        "regional_analysis": regional_res,
        "recommendation": final_rec
    }

# Untuk debugging langsung
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)