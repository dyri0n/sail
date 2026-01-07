<script lang="ts">
  export let title: string;
  export let value: string | number;
  export let change: number | null = null; // Cambio porcentual vs período anterior
  export let subtitle: string = '';
  export let icon: 'up' | 'down' | 'neutral' = 'neutral';
  export let color: 'red' | 'green' | 'blue' | 'orange' | 'purple' = 'blue';

  const colorClasses = {
    red: 'from-red-600/20 to-red-700/20 text-red-400',
    green: 'from-green-600/20 to-green-700/20 text-green-400',
    blue: 'from-blue-600/20 to-blue-700/20 text-blue-400',
    orange: 'from-orange-600/20 to-orange-700/20 text-orange-400',
    purple: 'from-purple-600/20 to-purple-700/20 text-purple-400'
  };

  const borderColors = {
    red: 'border-red-500/50',
    green: 'border-green-500/50',
    blue: 'border-blue-500/50',
    orange: 'border-orange-500/50',
    purple: 'border-purple-500/50'
  };

  function formatChange(val: number): string {
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(1)}%`;
  }
</script>

<div class="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-2xl border border-gray-700 hover:{borderColors[color]} transition-all duration-300 shadow-lg hover:shadow-xl">
  <div class="flex items-start justify-between mb-4">
    <div class="flex-1">
      <p class="text-gray-400 text-sm font-medium mb-1">{title}</p>
      <h3 class="text-3xl font-bold text-white">{value}</h3>
      {#if subtitle}
        <p class="text-gray-500 text-xs mt-1">{subtitle}</p>
      {/if}
    </div>
    
    <div class="h-12 w-12 bg-gradient-to-br {colorClasses[color]} rounded-xl flex items-center justify-center">
      {#if icon === 'up'}
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
        </svg>
      {:else if icon === 'down'}
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
        </svg>
      {:else}
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
      {/if}
    </div>
  </div>

  {#if change !== null}
    <div class="flex items-center text-sm">
      {#if change > 0}
        <svg class="w-4 h-4 text-green-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
        </svg>
        <span class="text-green-400 font-medium">{formatChange(change)}</span>
      {:else if change < 0}
        <svg class="w-4 h-4 text-red-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
        </svg>
        <span class="text-red-400 font-medium">{formatChange(change)}</span>
      {:else}
        <span class="text-gray-400 font-medium">Sin cambio</span>
      {/if}
      <span class="text-gray-500 ml-2">vs período anterior</span>
    </div>
  {/if}
</div>
