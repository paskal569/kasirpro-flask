 // ============================================================
//  pelanggan.js
//  Versi: perbaikan + pengembangan dari kode Anda
// ============================================================


// ============================================================
// 1. FILTER WAKTU
//    Klik tombol → active berpindah → fetchData dipanggil
// ============================================================
function initFilter() {
  const buttons = document.querySelectorAll('.btn-filter');

  buttons.forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();

      buttons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      const periode = this.textContent.trim();
      console.log('Filter dipilih:', periode);

      fetchData(periode); // ← sebelumnya cuma TODO, sekarang sudah dipanggil
    });
  });
}


// ============================================================
// 2. CARD SUMMARY — klik kartu untuk highlight
// ============================================================
function initCardSummary() {
  const cards = document.querySelectorAll('.card-summary');

  cards.forEach(card => {
    card.addEventListener('click', function () {
      cards.forEach(c => c.classList.remove('active'));
      this.classList.add('active');

      const id = this.id;
      console.log('Kartu dipilih:', id);

      // TODO: tampilkan detail berdasarkan kartu yang dipilih
    });
  });
}


// ============================================================
// 3. PROGRESS BAR CONVERSION RATE
//    PERBAIKAN: fungsi sebelumnya tidak ditutup dengan benar
//    dan setTimeout mengambang di luar fungsi
// ============================================================
function initProgressBars() {
  const bars = document.querySelectorAll('.conversion-item__bar-fill');

  bars.forEach(bar => {
    const target = bar.style.width;  // ambil target dari HTML style="width: X%"
    bar.style.width = '0%';          // reset ke 0 dulu

    setTimeout(() => {
      bar.style.transition = 'width 0.8s ease';
      bar.style.width = target;      // animasi ke target
    }, 300);
  });
}


// ============================================================
// 4. GRAFIK JAM (Chart.js)
//    PERBAIKAN: options.scales sebelumnya tidak lengkap (kurung tidak ditutup)
//    Sekarang grafik disimpan ke variabel global agar bisa di-update
// ============================================================
let grafikInstance = null; // simpan instance agar bisa di-destroy saat update

function initGrafik(labels = [], dataValues = []) {
  const canvas = document.getElementById('grafikJam');
  if (!canvas) return;

  // Kalau grafik sudah ada, hancurkan dulu sebelum buat baru
  if (grafikInstance) {
    grafikInstance.destroy();
  }

  const ctx = canvas.getContext('2d');

  grafikInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ['08','09','10','11','12','13','14','15','16','17','18','19','20'],
      datasets: [{
        label: 'Pengunjung',
        data: dataValues.length ? dataValues : [0, 5, 20, 45, 80, 60, 40, 55, 70, 50, 30, 15, 5],
        backgroundColor: 'rgba(59, 130, 246, 0.15)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        pointBackgroundColor: '#fff',
        pointBorderColor: '#3b82f6',
        pointRadius: 4,
        tension: 0.4,  // kurva halus
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true },
        x: { grid: { display: false } }
      }
    }
  });
}


// ============================================================
// 5. UPDATE GRAFIK — panggil ini saat data baru datang dari server
//    PERBAIKAN: sebelumnya fungsi uddategrafik() membuat Chart baru
//    tanpa destroy yang lama → grafik tumpang tindih
// ============================================================
function updateGrafik(labels, dataValues) {
  if (!grafikInstance) {
    initGrafik(labels, dataValues);
    return;
  }

  grafikInstance.data.labels = labels;
  grafikInstance.data.datasets[0].data = dataValues;
  grafikInstance.update(); // update tanpa destroy → animasi lebih halus
}


// ============================================================
// 6. UPDATE SUMMARY CARDS — isi nilai kartu dari data server
//    TODO: sesuaikan key sesuai response JSON Flask Anda
// ============================================================
function updateSummaryCards(summary) {
  // Contoh: summary = { pengunjung: 1876, pembelian: 950, durasi: '12 mnt', conversion: '50%' }
  const map = {
    'card-1': summary.pengunjung,
    'card-2': summary.pembelian,
    'card-3': summary.durasi,
    'card-4': summary.conversion,
  };

  Object.entries(map).forEach(([id, nilai]) => {
    const el = document.querySelector(`#${id} .card-summary__value`);
    if (el && nilai !== undefined) el.textContent = nilai;
  });
}


// ============================================================
// 7. UPDATE TABEL — isi tbody dari data server
//    TODO: sesuaikan kolom dengan response JSON Flask Anda
// ============================================================
function updateTabel(rows) {
  const tbody = document.querySelector('.section-table tbody');
  if (!tbody) return;

  tbody.innerHTML = ''; // kosongkan dulu

  rows.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.jam         || '-'}</td>
      <td>${item.total       || 0}</td>
      <td>${item.pembeli     || 0}</td>
      <td>${item.jumlah      || 0}</td>
      <td>${item.tidak_beli  || 0}</td>
      <td>${item.conversion  || '-'}</td>
      <td>${item.status      || '-'}</td>
    `;
    tbody.appendChild(tr);
  });
}


// ============================================================
// 8. FETCH DATA DARI BACKEND
//    PERBAIKAN: sebelumnya fungsi todos() dan updateData()
//    terperangkap di dalam fetchData() → sekarang dipisah keluar
// ============================================================
async function fetchData(periode) {
  try {
    const response = await fetch(`/api/pelanggan?periode=${encodeURIComponent(periode)}`);

    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

    const data = await response.json();
    console.log('Data dari server:', data);

    // Update semua komponen setelah data datang
    if (data.summary)  updateSummaryCards(data.summary);
    if (data.grafik)   updateGrafik(data.grafik.labels, data.grafik.values);
    if (data.tabel)    updateTabel(data.tabel);

  } catch (error) {
    console.error('Gagal fetch data:', error);
  }
}


// ============================================================
// 9. INIT — jalankan semua saat halaman siap
//    PERBAIKAN: todos() dan updateData() dihapus karena duplikasi
//    dan tidak punya HTML target yang jelas di halaman ini
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  initFilter();
  initCardSummary();
  initProgressBars();
  initGrafik();
});