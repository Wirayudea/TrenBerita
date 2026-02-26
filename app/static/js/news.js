let currentPage = 1;
// Perbesar jumlah berita per halaman agar lebih banyak sumber terlihat
const pageSize = 40;

async function showMessage(text, type = 'info') {
  const el = document.getElementById('message');
  el.textContent = text;
  el.className = 'message ' + type;
  el.style.display = 'block';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleString('id-ID');
}

async function loadNews(page) {
  const skip = (page - 1) * pageSize;
  const res = await fetch(`/api/news/page?skip=${skip}&limit=${pageSize}`);
  if (!res.ok) {
    showMessage('Gagal memuat berita', 'error');
    return;
  }
  const data = await res.json();

  const tbody = document.querySelector('#news-table tbody');
  tbody.innerHTML = '';
  data.items.forEach(item => {
    const tr = document.createElement('tr');

    const tdSource = document.createElement('td');
    tdSource.textContent = item.source || '';
    tr.appendChild(tdSource);

    const tdTitle = document.createElement('td');
    tdTitle.textContent = item.title || '';
    tr.appendChild(tdTitle);

    const tdUrl = document.createElement('td');
    if (item.url) {
      const a = document.createElement('a');
      a.href = item.url;
      a.target = '_blank';
      a.textContent = 'Link';
      tdUrl.appendChild(a);
    }
    tr.appendChild(tdUrl);

    const tdDate = document.createElement('td');
    tdDate.textContent = formatDate(item.published_at || item.created_at);
    tr.appendChild(tdDate);

    const tdCluster = document.createElement('td');
    tdCluster.textContent = item.cluster_label != null ? item.cluster_label : '';
    tr.appendChild(tdCluster);

    const tdRecTitle = document.createElement('td');
    tdRecTitle.textContent = item.recommended_title || '';
    tr.appendChild(tdRecTitle);

    tbody.appendChild(tr);
  });

  const totalPages = Math.max(1, Math.ceil(data.total / pageSize));
  currentPage = Math.min(page, totalPages);

  document.getElementById('page-info').textContent = `Halaman ${currentPage} / ${totalPages}`;
  document.getElementById('prev-page').disabled = currentPage <= 1;
  document.getElementById('next-page').disabled = currentPage >= totalPages;
}

async function runScrape() {
  showMessage('Memulai scraping...', 'info');
  const res = await fetch('/api/scrape/run', { method: 'POST' });
  if (!res.ok) {
    showMessage('Scraping gagal', 'error');
    return;
  }
  const data = await res.json();
  showMessage(`Scraping selesai. Berita baru: ${data.inserted}`, 'success');
  loadNews(currentPage);
}

async function deleteAllNews() {
  const ok = window.confirm('Yakin ingin menghapus SEMUA berita? Tindakan ini tidak bisa dibatalkan.');
  if (!ok) return;

  showMessage('Menghapus semua berita...', 'info');
  const res = await fetch('/api/news/all', { method: 'DELETE' });
  if (!res.ok) {
    showMessage('Gagal menghapus semua berita', 'error');
    return;
  }
  const data = await res.json();
  showMessage(`Berhasil menghapus ${data.deleted} berita.`, 'success');
  loadNews(1);
}

async function uploadCsv(event) {
  event.preventDefault();
  const fileInput = document.getElementById('csv-file');
  if (!fileInput.files.length) {
    showMessage('Pilih file CSV terlebih dahulu', 'warning');
    return;
  }
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  showMessage('Mengupload CSV...', 'info');
  const res = await fetch('/api/news/upload-csv', {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    let msg = 'Upload CSV gagal';
    try {
      const err = await res.json();
      if (err.detail) msg += `: ${err.detail}`;
    } catch (e) {}
    showMessage(msg, 'error');
    return;
  }

  const data = await res.json();
  showMessage(`Upload selesai. Ditambah: ${data.inserted}, dilewati: ${data.skipped}`, 'success');
  fileInput.value = '';
  loadNews(1);
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-scrape').addEventListener('click', runScrape);
  const delAllBtn = document.getElementById('btn-delete-all');
  if (delAllBtn) {
    delAllBtn.addEventListener('click', deleteAllNews);
  }
  document.getElementById('csv-form').addEventListener('submit', uploadCsv);
  document.getElementById('prev-page').addEventListener('click', () => {
    if (currentPage > 1) loadNews(currentPage - 1);
  });
  document.getElementById('next-page').addEventListener('click', () => {
    loadNews(currentPage + 1);
  });

  loadNews(1);
});
