<script setup>
defineProps({
  scorecard: Array
});

// Helper warna badge
const getBadgeInfo = (status) => {
  switch (status) {
    case 'good': return { class: 'bg-green-100 text-green-800 border-green-200', icon: '✅' };
    case 'warning': return { class: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: '⚠️' };
    case 'bad': return { class: 'bg-red-100 text-red-800 border-red-200', icon: '🚨' };
    default: return { class: 'bg-gray-100 text-gray-800 border-gray-200', icon: 'ℹ️' };
  }
};
</script>

<template>
  <div class="overflow-hidden border border-gray-200 rounded-xl shadow-sm bg-white">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Faktor Risiko</th>
          <th class="px-4 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Nilai Aktual</th>
          <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Analisis AI</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-100">
        <tr v-for="(item, index) in scorecard" :key="index" class="hover:bg-slate-50 transition-colors">
          <td class="px-4 py-3 text-sm font-semibold text-gray-700">
            {{ item.feature }}
          </td>
          <td class="px-4 py-3 text-sm text-center font-mono text-gray-600 bg-gray-50/50">
            {{ item.value_display }}
          </td>
          <td class="px-4 py-3 text-sm">
            <div class="flex items-center gap-2">
              <span 
                class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border shadow-sm"
                :class="getBadgeInfo(item.status).class"
              >
                {{ getBadgeInfo(item.status).icon }} {{ item.insight }}
              </span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>