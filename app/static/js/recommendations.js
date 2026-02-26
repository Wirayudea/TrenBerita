function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleString('id-ID');
}

async function loadRecommendations() {
  const res = await fetch('/api/news/page?skip=0&limit=100&has_recommendation=true');
  if (!res.ok) {
    console.error('Gagal mengambil data rekomendasi judul');
    return;
  }
  const data = await res.json();

  const tbody = document.querySelector('#recom-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (!data.items.length) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 6;
    td.textContent = 'Belum ada rekomendasi judul. Jalankan proses analisis terlebih dahulu.';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  data.items.forEach(item => {
    const tr = document.createElement('tr');

    const tdSource = document.createElement('td');
    tdSource.textContent = item.source || '';
    tr.appendChild(tdSource);

    const tdTitle = document.createElement('td');
    tdTitle.textContent = item.title || '';
    tr.appendChild(tdTitle);

    const tdRec = document.createElement('td');
    tdRec.textContent = item.recommended_title || '';
    tr.appendChild(tdRec);

    const tdCluster = document.createElement('td');
    tdCluster.textContent = item.cluster_label != null ? item.cluster_label : '';
    tr.appendChild(tdCluster);

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

window.addEventListener('DOMContentLoaded', loadRecommendations);
