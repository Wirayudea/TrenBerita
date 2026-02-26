function showAnalysisMessage(text, type = 'info') {
  const el = document.getElementById('analysis-message');
  if (!el) return;
  el.textContent = text;
  el.className = 'message ' + type;
  el.style.display = 'block';
}

async function runAnalysis(event) {
  event.preventDefault();

  const topicsInput = document.getElementById('n-topics');
  const clustersInput = document.getElementById('n-clusters');
  const nTopics = parseInt(topicsInput.value, 10) || 5;
  const nClusters = parseInt(clustersInput.value, 10) || 5;

  showAnalysisMessage('Menjalankan analisis... mohon tunggu.', 'info');

  const btn = event.target.querySelector('button[type="submit"]');
  if (btn) {
    btn.disabled = true;
  }

  try {
    const res = await fetch(`/api/analysis/run?n_topics=${nTopics}&n_clusters=${nClusters}`, {
      method: 'POST'
    });

    if (!res.ok) {
      showAnalysisMessage('Analisis gagal dijalankan.', 'error');
      if (btn) btn.disabled = false;
      return;
    }

    const data = await res.json();
    const msg = data.message || 'Analisis selesai.';
    const total = data.total_articles ?? 'tidak diketahui';

    showAnalysisMessage(`${msg} Total berita dianalisis: ${total}.`, 'success');

    const summary = document.getElementById('analysis-summary');
    if (summary) {
      summary.textContent = `Terakhir dijalankan dengan ${nTopics} topik dan ${nClusters} cluster. Total berita dianalisis: ${total}.`;
    }
  } catch (e) {
    console.error(e);
    showAnalysisMessage('Terjadi kesalahan tak terduga saat menjalankan analisis.', 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('analysis-form');
  if (form) {
    form.addEventListener('submit', runAnalysis);
  }
});
