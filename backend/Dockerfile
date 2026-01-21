# Gunakan Python 3.10 yang ringan
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# 1. Install Dependencies dulu (agar cache layer optimal)
# Kita copy requirements dari folder backend lokal ke root container sementara
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy Source Code
# PENTING: Kita copy 'backend' dan 'ml_engine' agar struktur folder
# tetap sama seperti di laptop Anda (/app/backend dan /app/ml_engine)
# sehingga logika 'BASE_DIR' di services.py tetap jalan.
COPY backend/ /app/backend/
COPY ml_engine/ /app/ml_engine/

# Expose port
EXPOSE 8000

# Perintah untuk menjalankan aplikasi
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]