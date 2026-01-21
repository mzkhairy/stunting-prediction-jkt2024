<script setup>
import { computed } from 'vue';

const props = defineProps({
  value: Number, // 0 - 100
  label: String, // "Normal", "Stunting"
  color: String, // Hex color code
  hint: String   // "Normal (Hati-hati)" - KITA HAPUS DARI TAMPILAN
});

// Posisi marker segitiga (User Result)
const markerStyle = computed(() => ({
  left: `${props.value}%`,
  borderBottomColor: props.color // Segitiga menghadap ke atas
}));
</script>

<template>
  <div class="w-full my-8 px-2">
    <div class="flex justify-between mb-8 text-sm font-bold tracking-wide items-end">
      <span class="text-gray-600 text-base">Status Fisik: <span :style="{ color: color }" class="text-2xl ml-1">{{ label }}</span></span>
      </div>

    <div class="relative h-14 w-full">
      
      <div class="absolute -top-7 z-10 flex flex-col items-center" style="left: 33%; transform: translateX(-50%);">
        <div class="bg-white border border-red-200 text-red-600 px-2 py-0.5 rounded shadow-sm text-[10px] font-bold whitespace-nowrap">
          Batas Stunting (-2 SD)
        </div>
        <div class="w-px h-2 bg-red-200"></div>
      </div>

      <div class="absolute -top-7 z-10 flex flex-col items-center" style="left: 50%; transform: translateX(-50%);">
        <div class="bg-white border border-yellow-200 text-yellow-600 px-2 py-0.5 rounded shadow-sm text-[10px] font-bold whitespace-nowrap">
          Batas Waspada (-1 SD)
        </div>
         <div class="w-px h-2 bg-yellow-200"></div>
      </div>

      <div class="relative h-6 w-full rounded-full bg-gray-100 overflow-hidden shadow-inner border border-gray-200">
        <div class="absolute inset-0 bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 opacity-90"></div>
        
        <div class="absolute top-0 bottom-0 border-l border-white/50 border-dashed" style="left: 33%"></div> 
        <div class="absolute top-0 bottom-0 border-l border-white/50 border-dashed" style="left: 50%"></div>
      </div>

      <div class="relative w-full h-4 -mt-1">
        <div 
          class="absolute w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-b-[12px] transition-all duration-700 ease-out transform -translate-x-1/2 drop-shadow-md z-20"
          :style="markerStyle"
        ></div>
        <div 
            class="absolute top-4 transition-all duration-700 ease-out transform -translate-x-1/2 text-[10px] font-bold text-gray-800 bg-white/90 border border-gray-100 px-2 py-0.5 rounded shadow-sm"
             :style="{ left: `${value}%` }"
        >
            Anak Anda
        </div>
      </div>

    </div>
    
    <div class="flex justify-between text-[9px] text-gray-400 mt-5 font-mono font-medium tracking-tighter">
        <span>Sangat Pendek (-3SD)</span>
        <span>Ideal (+2SD)</span>
    </div>
  </div>
</template>