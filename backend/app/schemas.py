# backend/app/schemas.py

from pydantic import BaseModel
from typing import List, Optional

class ChildInput(BaseModel):
    umur_bulan: int
    jenis_kelamin: int  # 0: Perempuan, 1: Laki-laki
    tinggi_badan: float
    berat_badan: float
    kecamatan: str
    kelurahan: str

# --- OUTPUT SPECTRUM WHO (Updated) ---
class WHOAnalysis(BaseModel):
    status_code: str    # 'normal', 'stunting', 'severely_stunting'
    status_label: str   # Label Utama: 'Normal', 'Pendek', dll
    z_score: float      # Nilai matematis (-1.5, -2.1, dll)
    
    # Data Visualisasi Spectrum
    spectrum_value: float    # 0 - 100 (Posisi marker di bar)
    spectrum_color: str      # Warna marker (green, yellow, orange, red)
    spectrum_hint: str       # Insight posisi: "Normal tapi hati-hati", "Stunting Ringan"

# --- OUTPUT REGIONAL (Updated) ---
class ScorecardItem(BaseModel):
    feature: str    # Nama Fitur (Bhs Sederhana)
    value_display: str # Nilai yang diformat (misal "12%")
    status: str     # 'good', 'warning', 'bad', 'neutral'
    insight: str    # Penjelasan sederhana ("Sesuai rata-rata", "Perlu perhatian")

class RegionalInsight(BaseModel):
    risk_level: str
    risk_code: int
    scorecard: List[ScorecardItem]
    narrative: str

class PredictionResponse(BaseModel):
    child_analysis: WHOAnalysis
    regional_analysis: RegionalInsight
    recommendation: str