let topicsData = [];
let topicChart = null;

async function fetchTopics() {
  const res = await fetch('/api/analysis/topics');
  if (!res.ok) {
    console.error('Gagal mengambil data topik');
    return [];
  }
  return await res.json();
}

function renderTopicOptions() {
  const select = document.getElementById('topic-select');
  select.innerHTML = '';
  topicsData.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t.topic;
    opt.textContent = `Topik ${t.topic}`;
    select.appendChild(opt);
  });
}

function renderTopicChart(topicIndex) {
  const topic = topicsData.find(t => t.topic === topicIndex);
  if (!topic) return;

  const labels = topic.terms.map(t => t[0]);
  const values = topic.terms.map(t => t[1]);

  const ctx = document.getElementById('topicChart').getContext('2d');

  if (topicChart) {
    topicChart.destroy();
  }

  topicChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: `Bobot kata untuk Topik ${topicIndex}`,
        data: values,
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(37, 99, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });

  const listDiv = document.getElementById('topic-terms');
  listDiv.innerHTML = '<h3>Kata kunci topik</h3>' +
    '<ul>' + topic.terms.map(t => `<li>${t[0]} (bobot: ${t[1].toFixed(4)})</li>`).join('') + '</ul>';
}

window.addEventListener('DOMContentLoaded', async () => {
  topicsData = await fetchTopics();
  if (!topicsData.length) {
    const div = document.getElementById('topic-terms');
    if (div) div.textContent = 'Belum ada hasil LDA. Jalankan proses analisis terlebih dahulu.';
    return;
  }
  renderTopicOptions();

  const select = document.getElementById('topic-select');
  select.addEventListener('change', () => {
    const idx = parseInt(select.value, 10);
    renderTopicChart(idx);
  });

  // render topik pertama secara default
  renderTopicChart(topicsData[0].topic);
  select.value = topicsData[0].topic;
});
