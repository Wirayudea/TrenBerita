async function loadDashboard() {
  const res = await fetch('/api/dashboard');
  const data = await res.json();

  document.getElementById('total-articles').innerText = data.total_articles;

  const clusterCtx = document.getElementById('clusterChart').getContext('2d');
  const clusterLabels = data.clusters.map(c => 'Cluster ' + c.cluster);
  const clusterData = data.clusters.map(c => c.count);

  new Chart(clusterCtx, {
    type: 'bar',
    data: {
      labels: clusterLabels,
      datasets: [{
        label: 'Jumlah Berita per Cluster',
        data: clusterData,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: { scales: { y: { beginAtZero: true } } }
  });

  const timelineCtx = document.getElementById('timelineChart').getContext('2d');
  const timelineLabels = data.timeline.map(t => t.date);
  const timelineData = data.timeline.map(t => t.count);

  new Chart(timelineCtx, {
    type: 'line',
    data: {
      labels: timelineLabels,
      datasets: [{
        label: 'Jumlah Berita per Hari',
        data: timelineData,
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.2
      }]
    }
  });
}

window.addEventListener('DOMContentLoaded', loadDashboard);
