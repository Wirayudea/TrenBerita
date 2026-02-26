async function fetchDashboard() {
  const res = await fetch('/api/dashboard');
  if (!res.ok) {
    console.error('Gagal mengambil data dashboard');
    return null;
  }
  return await res.json();
}

let barChart = null;
let pieChart = null;
let clustersCache = [];

function renderClusterCharts(clusters) {
  const labels = clusters.map(c => 'Cluster ' + c.cluster);
  const values = clusters.map(c => c.count);

  const barCtx = document.getElementById('clusterBarChart').getContext('2d');
  const pieCtx = document.getElementById('clusterPieChart').getContext('2d');

  if (barChart) barChart.destroy();
  if (pieChart) pieChart.destroy();

  barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Jumlah Berita per Cluster',
        data: values,
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
        borderColor: 'rgba(22, 163, 74, 1)',
        borderWidth: 1
      }]
    },
    options: { scales: { y: { beginAtZero: true } } }
  });

  const colors = [
    'rgba(59, 130, 246, 0.7)',
    'rgba(234, 179, 8, 0.7)',
    'rgba(248, 113, 113, 0.7)',
    'rgba(52, 211, 153, 0.7)',
    'rgba(251, 146, 60, 0.7)',
    'rgba(192, 132, 252, 0.7)'
  ];

  pieChart = new Chart(pieCtx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: labels.map((_, i) => colors[i % colors.length])
      }]
    }
  });
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleString('id-ID');
}

async function loadClusterNews(cluster) {
  const res = await fetch(`/api/news/page?skip=0&limit=50&cluster_label=${cluster}`);
  if (!res.ok) {
    console.error('Gagal mengambil berita untuk cluster', cluster);
    return;
  }
  const data = await res.json();

  const tbody = document.querySelector('#cluster-news-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  data.items.forEach(item => {
    const tr = document.createElement('tr');

    const tdCluster = document.createElement('td');
    tdCluster.textContent = item.cluster_label != null ? item.cluster_label : '';
    tr.appendChild(tdCluster);

    const tdSource = document.createElement('td');
    tdSource.textContent = item.source || '';
    tr.appendChild(tdSource);

    const tdTitle = document.createElement('td');
    tdTitle.textContent = item.title || '';
    tr.appendChild(tdTitle);

    const tdDate = document.createElement('td');
    tdDate.textContent = formatDate(item.published_at || item.created_at);
    tr.appendChild(tdDate);

    const tdUrl = document.createElement('td');
    if (item.url) {
      const a = document.createElement('a');
      a.href = item.url;
      a.target = '_blank';
      a.textContent = 'Link';
      tdUrl.appendChild(a);
    }
    tr.appendChild(tdUrl);

    tbody.appendChild(tr);
  });
}

function initClusterSelector(clusters) {
  const select = document.getElementById('cluster-select');
  if (!select) return;

  select.innerHTML = '';
  clusters.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.cluster;
    opt.textContent = `Cluster ${c.cluster} (${c.count})`;
    select.appendChild(opt);
  });

  select.addEventListener('change', () => {
    const val = parseInt(select.value, 10);
    if (!isNaN(val)) {
      loadClusterNews(val);
    }
  });

  if (clusters.length) {
    select.value = clusters[0].cluster;
    loadClusterNews(clusters[0].cluster);
  }
}

window.addEventListener('DOMContentLoaded', async () => {
  const data = await fetchDashboard();
  if (!data || !data.clusters || !data.clusters.length) {
    console.warn('Belum ada data cluster. Jalankan analisis terlebih dahulu.');
    return;
  }
  clustersCache = data.clusters;
  renderClusterCharts(clustersCache);
  initClusterSelector(clustersCache);
});
