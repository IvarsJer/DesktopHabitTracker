// app/static/js/charts.js
document.addEventListener("DOMContentLoaded", async () => {
  const canvases = document.querySelectorAll("canvas.spark");
  if (!window.Chart) {
    console.error("Chart.js not loaded");
    return;
  }

  for (const el of canvases) {
    try {
      const existing = Chart.getChart ? Chart.getChart(el) : null;
      if (existing) existing.destroy();

      const habitId = el.dataset.habit;
      const color   = el.dataset.color || "#344CB7";

      const res = await fetch(`/api/stats?habit_id=${encodeURIComponent(habitId)}&range=daily&days=90`);
      if (!res.ok) {
        console.error("Stats fetch failed", habitId, res.status);
        continue;
      }
      const data = await res.json();
      const labels = (data.points || []).map(p => p.date);
      const values = (data.points || []).map(p => p.value);

      const ctx = el.getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [{
            data: values,
            borderWidth: 2,
            borderColor: color,
            pointRadius: 0,
            tension: 0.35,
            fill: true,
            backgroundColor: hexToRgba(color, 0.12),
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          plugins: { legend: { display: false }, tooltip: { enabled: true } },
          scales: { x: { display: false }, y: { display: false } },
        }
      });
    } catch (e) {
      console.error("Chart render error", e);
    }
  }
});

function hexToRgba(hex, a) {
  const m = hex.replace("#","").match(/.{1,2}/g).map(h => parseInt(h,16));
  return `rgba(${m[0]},${m[1]},${m[2]},${a})`;
}
