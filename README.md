# 🛡️ StuntGuard Jakarta

![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Vue.js%20%7C%20Docker-blue)
![Data Source](https://img.shields.io/badge/Data-SatuData%20Jakarta-orange)

**StuntGuard Jakarta** adalah sistem dashboard cerdas untuk memprediksi risiko stunting pada balita dan melakukan profiling kesehatan wilayah di DKI Jakarta.

Sistem ini menggabungkan **Standar Antropometri WHO** (Z-Score) untuk analisis individu dan **Machine Learning (K-Means Clustering)** untuk memetakan karakteristik wilayah berdasarkan 6 indikator kesehatan utama.

---

## ✨ Fitur Utama

- **👶 WHO Growth Calculator:** Analisis status gizi balita (Normal, Stunting, Severely Stunting) menggunakan standar deviasi WHO.
- **📊 Spectrum Meter Visualizer:** Visualisasi posisi pertumbuhan anak dalam grafik spektrum warna yang intuitif (dengan batas -2 SD dan -1 SD).
- **🗺️ Regional Insight Engine:** Analisis otomatis risiko wilayah (Kecamatan & Kelurahan) menggunakan data 2024 open-source satudata.jakarta.go.id 
- **🧠 Smart Recommendation:** Rekomendasi kebijakan kesehatan yang spesifik berdasarkan profil risiko wilayah

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
| :--- | :--- |
| **Frontend** | Vue.js 3 (Composition API), Vite, Tailwind CSS v4 |
| **Backend** | Python FastAPI, Uvicorn, Pydantic |
| **Machine Learning** | Scikit-learn (K-Means), Pandas, Joblib |
| **Infrastructure** | Docker, Docker Compose, Nginx |

---

## 🚀 Panduan Instalasi
Panduan ini mencakup langkah dari nol, termasuk instalasi Docker dan persiapan sistem.

### Langkah 1: Persiapan Lingkungan (Prerequisites)

Anda membutuhkan **Docker** dan **Git** untuk menjalankan aplikasi ini.

#### 🅰️ Untuk Pengguna Windows (Wajib Aktifkan WSL2)
Docker di Windows berjalan lebih optimal menggunakan WSL2 (Windows Subsystem for Linux).

1.  **Aktifkan Virtualization:** Pastikan fitur Virtualization (VT-x/AMD-V) sudah aktif di BIOS laptop Anda.
2.  **Install WSL2:**
    * Buka **PowerShell** sebagai Administrator (Klik kanan -> Run as Administrator).
    * Ketik perintah:
        ```powershell
        wsl --install
        ```
    * Tunggu proses selesai, lalu **Restart** komputer Anda.
    * Setelah restart, jendela Ubuntu mungkin terbuka otomatis untuk setup username/password (ikuti saja).
3.  **Install Docker Desktop:**
    * Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
    * Install seperti biasa.
    * Buka Docker Desktop -> **Settings** (ikon gerigi) -> **General**.
    * Pastikan centang **"Use the WSL 2 based engine"**.
    * Klik **Apply & Restart**.

#### 🅱️ Untuk Pengguna Mac / Linux
* **Mac:** Download & Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/).
* **Linux:** Ikuti panduan instalasi Docker Engine untuk distro Anda (Ubuntu/Debian/CentOS).

---

### Langkah 2: Download Project (Clone)

Buka terminal (Command Prompt / PowerShell / Terminal), lalu jalankan:


#### 1. Clone repository ini
git clone [https://github.com/USERNAME_ANDA/stunting-prediction-jakarta.git](https://github.com/USERNAME_ANDA/stunting-prediction-jakarta.git)

#### 2. Masuk ke folder project
cd stunting-prediction-jakarta
Langkah 3: Menjalankan Aplikasi (Mode Docker) 🐳
Ini adalah cara termudah. Docker akan otomatis menginstall Python, Node.js, dan semua library yang dibutuhkan di dalam container yang terisolasi.

Pastikan aplikasi Docker Desktop sudah terbuka dan berstatus "Running".

Jalankan perintah berikut di terminal root folder project:

```Bash
docker compose up --build
```
Tunggu proses build selesai (mungkin memakan waktu 5-10 menit tergantung kecepatan internet untuk download image).

Jika terminal menampilkan log seperti Uvicorn running... dan Ready in..., berarti aplikasi sudah siap.

Akses Aplikasi:

Frontend (Dashboard): Buka browser ke http://localhost:5173

Backend (API Docs): Buka browser ke http://localhost:8000/docs

Untuk mematikan aplikasi, tekan Ctrl + C di terminal, atau jalankan docker compose down.

#### Langkah 4: Menjalankan Aplikasi (Mode Manual / Development)
Gunakan cara ini jika Anda ingin mengedit kode (tanpa Docker).

A. Setup Backend
Pastikan Anda memiliki Python 3.10+ terinstall.

```
cd backend
```
#### 1. Buat Virtual Environment
python -m venv venv

#### 2. Aktifkan Virtual Environment
#### Windows:
venv\Scripts\activate
#### Mac/Linux:
source venv/bin/activate

#### 3. Install Dependencies
pip install -r requirements.txt

#### 4. Generate Model Clustering (PENTING: Jalankan ini sekali di awal)
python ../ml_engine/scripts/2_build_cluster_engine.py

#### 5. Jalankan Server Backend
uvicorn app.main:app --reload
Backend berjalan di http://localhost:8000

B. Setup Frontend
Pastikan Anda memiliki Node.js v20 atau v22 terinstall (Wajib untuk Tailwind v4).

```
cd frontend
```
#### 1. Install Dependencies
npm install

#### 2. Jalankan Server Frontend
npm run dev
Frontend berjalan di https://www.google.com/search?q=http://localhost:5173

📂 Struktur Project
```
stunting-prediction-jakarta/
├── backend/                # Kode Python FastAPI
│   ├── app/
│   │   ├── main.py         # Entry point API
│   │   ├── services.py     # Logika Bisnis & Insight Generator
│   │   └── schemas.py      # Struktur Data (Pydantic)
│   └── requirements.txt
├── frontend/               # Kode Vue.js 3
│   ├── src/
│   │   ├── components/     # SpectrumMeter.vue, InsightCard.vue
│   │   └── App.vue         # Halaman Utama
│   ├── Dockerfile
│   └── vite.config.js
├── ml_engine/              # Script Machine Learning
│   ├── data/               # Dataset CSV (Raw & Processed)
│   ├── scripts/            # Script Cleaning & Clustering
│   └── models/             # Output Model (.joblib)
├── docker-compose.yml      # Orkestrasi Docker
└── README.md
```
⚠️ Troubleshooting Umum
1. Error Address already in use

Port 8000 atau 5173 sedang dipakai aplikasi lain.

Solusi: Matikan proses tersebut atau ubah port di docker-compose.yml.

2. Error Frontend crypto.hash is not a function

Penyebab: Versi Node.js terlalu lama (misal Node 18).

Solusi: Pastikan Dockerfile Frontend menggunakan FROM node:22-alpine atau upgrade Node.js lokal Anda ke versi 20+.

3. Data Wilayah Tidak Muncul di Dropdown

Penyebab: Model .joblib belum terbentuk atau Backend gagal membaca file.

Solusi: Pastikan script ml_engine/scripts/2_build_cluster_engine.py sudah dijalankan minimal sekali (Docker otomatis menjalankannya jika sudah di-build image-nya dengan benar, namun pastikan file regional_map.joblib ada).

📄 Lisensi & Atribusi Data
Sumber Data: Dataset terbuka dari satudata.jakarta.go.id (Tahun 2024).

Project License: MIT License.