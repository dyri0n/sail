<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  
  Chart.register(...registerables);

  export let data: { labels: string[], datasets: { data: number[], backgroundColor?: string[] }[] };
  export let title: string = '';
  export let height: number = 300;

  let canvas: HTMLCanvasElement;
  let chart: Chart;

  onMount(() => {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    chart = new Chart(ctx, {
      type: 'pie',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: {
              color: '#E5E7EB',
              font: {
                size: 12
              },
              padding: 15
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
        }
      }
    });

    return () => {
      chart.destroy();
    };
  });

  $: if (chart && data) {
    chart.data = data;
    chart.update();
  }
</script>

<div style="height: {height}px; position: relative;">
  <canvas bind:this={canvas}></canvas>
</div>
