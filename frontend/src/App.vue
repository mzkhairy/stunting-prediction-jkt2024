<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import SpectrumMeter from './components/SpectrumMeter.vue';
import InsightCard from './components/InsightCard.vue';

// --- STATE ---
const form = ref({
  umur_bulan: '',
  jenis_kelamin: 1, // 1: Laki, 0: Perempuan
  tinggi_badan: '',
  berat_badan: '', 
  kecamatan: '',
  kelurahan: ''
});

const locations = ref({ kecamatan: [], kelurahan: [] });
const result = ref(null);
const loading = ref(false);
const errorMsg = ref('');

// --- API CONFIG ---
const API_URL = 'http://127.0.0.1:8000';

// 1. Load Lokasi saat web dibuka
onMounted(async () => {
  try {
    const res = await axios.get(`${API_URL}/locations`);
    locations.value = res.data;
  } catch (err) {
    console.error("Gagal load lokasi", err);
    errorMsg.value = "Gagal memuat data wilayah. Pastikan backend menyala dan script clustering sudah dijalankan.";
  }
});

// 2. Submit Analisis
const submitAnalysis = async () => {
  loading.value = true;
  errorMsg.value = '';
  result.value = null;

  // Validasi
  if (!form.value.umur_bulan || !form.value.tinggi_badan || !form.value.kecamatan) {
    errorMsg.value = "Mohon lengkapi data Umur, Tinggi, dan Kecamatan.";
    loading.value = false;
    return;
  }

  try {
    const payload = {
      umur_bulan: parseInt(form.value.umur_bulan),
      jenis_kelamin: parseInt(form.value.jenis_kelamin),
      tinggi_badan: parseFloat(form.value.tinggi_badan),
      berat_badan: parseFloat(form.value.berat_badan || 0),
      kecamatan: form.value.kecamatan,
      kelurahan: form.value.kelurahan || '' // Kelurahan boleh kosong kalau user lupa, backend handle
    };

    const res = await axios.post(`${API_URL}/predict`, payload);
    result.value = res.data;
    
    // Auto scroll ke hasil
    setTimeout(() => {
      document.getElementById('result-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);

  } catch (err) {
    errorMsg.value = "Terjadi kesalahan koneksi ke server.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-10 px-4 font-sans text-slate-800">
    <div class="max-w-4xl mx-auto space-y-10">
      
      <div class="text-center space-y-2">
        <h1 class="text-4xl font-extrabold text-blue-900 tracking-tight">StuntGuard <span class="text-blue-600">Jakarta</span></h1>
        <p class="text-lg text-gray-600">Prediksi Risiko Stunting & Profil Kesehatan Wilayah</p>
      </div>

      <div v-if="errorMsg" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-md" role="alert">
        <p class="font-bold">Error</p>
        <p>{{ errorMsg }}</p>
      </div>

      <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 md:p-8">
        <h2 class="text-xl font-bold text-gray-800 mb-6 flex items-center border-b pb-4">
          <span class="bg-blue-100 text-blue-600 p-2 rounded-lg mr-3 text-lg">📝</span>
          Input Data Balita
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="space-y-5">
            <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Parameter Fisik</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Umur (Bulan)</label>
                <input v-model="form.umur_bulan" type="number" placeholder="0-60" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border transition-all">
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Jenis Kelamin</label>
                <select v-model="form.jenis_kelamin" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border transition-all bg-white">
                  <option :value="1">Laki-laki</option>
                  <option :value="0">Perempuan</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Tinggi (cm)</label>
                <input v-model="form.tinggi_badan" type="number" step="0.1" placeholder="cth: 85.5" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border transition-all">
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">Berat (kg) <span class="text-xs font-normal text-gray-400">(Opsional)</span></label>
                <input v-model="form.berat_badan" type="number" step="0.1" placeholder="cth: 12.0" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border transition-all">
              </div>
            </div>
          </div>

          <div class="space-y-5">
            <h3 class="text-sm font-bold text-gray-400 uppercase tracking-wider">Lokasi Domisili</h3>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Kecamatan</label>
              <select v-model="form.kecamatan" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border transition-all bg-white">
                <option disabled value="">-- Pilih Kecamatan --</option>
                <option v-for="kec in locations.kecamatan" :key="kec" :value="kec">{{ kec }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Kelurahan</label>
              <select v-model="form.kelurahan" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border transition-all bg-white">
                <option disabled value="">-- Pilih Kelurahan --</option>
                <option v-for="kel in locations.kelurahan" :key="kel" :value="kel">{{ kel }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-4 border-t">
          <button 
            @click="submitAnalysis" 
            :disabled="loading"
            class="w-full md:w-auto md:float-right flex justify-center items-center py-3 px-8 border border-transparent rounded-xl shadow-lg text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transform hover:-translate-y-0.5 transition-all duration-200"
          >
            <span v-if="loading" class="animate-spin mr-2">⏳</span>
            {{ loading ? 'Sedang Menganalisis...' : 'Analisis Risiko Sekarang' }}
          </button>
          <div class="clear-both"></div>
        </div>
      </div>

      <div id="result-section" v-if="result" class="space-y-8 animate-fade-in pb-10">
        
        <div class="bg-white rounded-2xl shadow-xl p-6 md:p-8 border-l-8 transition-colors duration-500" :style="{ borderLeftColor: result.child_analysis.spectrum_color }">
          <div class="flex flex-col md:flex-row md:justify-between md:items-start mb-4">
            <div>
              <h3 class="text-xl font-bold text-gray-800">Analisis Pertumbuhan Fisik</h3>
              <p class="text-gray-500 text-sm mt-1">Menggunakan standar WHO (Z-Score: {{ result.child_analysis.z_score }})</p>
            </div>
            <div class="mt-3 md:mt-0 px-4 py-2 rounded-lg text-white font-bold text-sm shadow-md" :style="{ backgroundColor: result.child_analysis.spectrum_color }">
               {{ result.child_analysis.status_label }}
            </div>
          </div>
          
          <SpectrumMeter 
            :value="result.child_analysis.spectrum_value"
            :label="result.child_analysis.status_label"
            :color="result.child_analysis.spectrum_color"
            :hint="result.child_analysis.spectrum_hint"
          />
        </div>

        <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
          <div class="p-6 md:p-8 bg-gradient-to-b from-gray-50 to-white border-b">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-bold text-gray-800 flex items-center">
                <span class="mr-2">🗺️</span> Analisis Lingkungan
              </h3>
              <span 
                class="px-4 py-1.5 rounded-full text-sm font-bold border shadow-sm"
                :class="{
                  'bg-green-100 text-green-700 border-green-200': result.regional_analysis.risk_code === 0,
                  'bg-yellow-100 text-yellow-700 border-yellow-200': result.regional_analysis.risk_code === 1,
                  'bg-red-100 text-red-700 border-red-200': result.regional_analysis.risk_code === 2
                }"
              >
                {{ result.regional_analysis.risk_level }}
              </span>
            </div>
            
            <div class="p-5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-700 text-sm leading-relaxed whitespace-pre-line shadow-sm">
              {{ result.regional_analysis.narrative }}
            </div>
          </div>

          <div class="p-6 md:p-8">
            <h4 class="text-xs font-extrabold text-gray-400 uppercase tracking-widest mb-4">Rapor Kesehatan Wilayah (6 Faktor)</h4>
            <InsightCard :scorecard="result.regional_analysis.scorecard" />
          </div>
        </div>

        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl p-6 md:p-8 text-white relative overflow-hidden">
          <div class="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-white opacity-5 rounded-full blur-2xl"></div>
          
          <h3 class="text-xl font-bold flex items-center relative z-10 text-blue-200">
            <span class="mr-2 text-2xl">💡</span> Rekomendasi Tindakan
          </h3>
          <p class="mt-4 text-white text-lg font-medium leading-relaxed tracking-wide relative z-10">
            "{{ result.recommendation }}"
          </p>
        </div>

      </div>
      <footer class="mt-16 border-t border-gray-200 pt-6 pb-2 text-center">
        <p class="text-sm text-gray-500 font-medium">
          Data berdasarkan data open publik 
          <a 
            href="https://satudata.jakarta.go.id" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
          >
            satudata.jakarta.go.id
          </a> 
          @ 2024
        </p>
        <p class="text-xs text-gray-400 mt-1">
          Dibuat sebagai Simulasi Prediksi Risiko Stunting Jakarta
        </p>
      </footer>
    </div>
  </div>
</template>

<style>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>