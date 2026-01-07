<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  
  // Registrar componentes de Chart.js
  Chart.register(...registerables);

  export let data: { labels: string[], datasets: { label: string, data: number[], borderColor?: string, backgroundColor?: string }[] };
  export let title: string = '';
  export let height: number = 300;

  let canvas: HTMLCanvasElement;
  let chart: Chart;

  onMount(() => {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    chart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            labels: {
              color: '#E5E7EB',
              font: {
                size: 12
              }
            }
          },
          title: {
            display: !!title,
            text: title,
            color: '#F3F4F6',
            font: {
              size: 16,
              weight: 'bold'
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#9CA3AF'
            },
            grid: {
              color: 'rgba(156, 163, 175, 0.1)'
            }
          },
          y: {
            ticks: {
              color: '#9CA3AF'
            },
            grid: {
              color: 'rgba(156, 163, 175, 0.1)'
            }
          }
        }
      }
    });

    return () => {
      chart.destroy();
    };
  });

  // Actualizar el gráfico cuando cambien los datos
  $: if (chart && data) {
    chart.data = data;
    chart.update();
  }
</script>

<div style="height: {height}px; position: relative;">
  <canvas bind:this={canvas}></canvas>
</div>
