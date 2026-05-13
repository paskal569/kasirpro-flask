// ============================================================
//  laporan.js — KasirPro | Laporan Barang Keluar
// ============================================================

const PER_PAGE = 10;
let currentPage = 1;
let dataFiltered = [];

/* ── HELPER ── */
function formatRupiah(angka) {
  return 'Rp ' + (parseInt(angka) || 0).toLocaleString('id-ID');
}

/* ── LOAD & FILTER DATA ── */
function loadLaporan() {
  const db      = JSON.parse(localStorage.getItem('laporan_barang_keluar') || '[]');
  const search  = document.getElementById('search')?.value?.toLowerCase().trim() || '';
  const tglDari   = document.getElementById('tgl-dari')?.value || '';
  const tglSampai = document.getElementById('tgl-sampai')?.value || '';

  // Filter nama + tanggal
  dataFiltered = db.filter(item => {
    const cocokNama = item.nama.toLowerCase().includes(search);
    const cocokTgl  = (!tglDari || item.tanggal >= tglDari) &&
                      (!tglSampai || item.tanggal <= tglSampai);
    return cocokNama && cocokTgl;
  });

  currentPage = 1;
  renderStats();
  renderTable();
  renderPagination();
}

/* ── STATISTIK ── */
function renderStats() {
  const totalNilai = dataFiltered.reduce((s, r) => s + r.total, 0);
  const el = document.getElementById('total-data');
  const elNilai = document.getElementById('total-nilai');
  if (el)      el.textContent = dataFiltered.length + ' item';
  if (elNilai) elNilai.textContent = formatRupiah(totalNilai);
}

/* ── RENDER TABEL ── */
function renderTable() {
  const tbody = document.getElementById('laporan-body');
  if (!tbody) return;

  if (dataFiltered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding:40px; color:#94A3B8;">
          Tidak ada data barang keluar.
        </td>
      </tr>`;
    updateInfo(0, 0, 0);
    return;
  }

  const start     = (currentPage - 1) * PER_PAGE;
  const end       = start + PER_PAGE;
  const paginated = dataFiltered.slice(start, end);

  tbody.innerHTML = paginated.map(item => `
    <tr>
      <td>${item.tanggal}</td>
      <td>${item.nama}</td>
      <td>${item.kategori ?? '-'}</td>
      <td>${item.jumlah}</td>
      <td>${formatRupiah(item.harga)}</td>
      <td><strong>${formatRupiah(item.total)}</strong></td>
      <td>${item.kasir ?? 'Admin'}</td>
    </tr>
  `).join('');

  updateInfo(start + 1, Math.min(end, dataFiltered.length), dataFiltered.length);
}

/* ── INFO "Menampilkan X-Y dari Z data" ── */
function updateInfo(dari, sampai, total) {
  const el = document.getElementById('info-data');
  if (el) el.textContent = `Menampilkan ${dari} - ${sampai} dari ${total} data`;
}

/* ── PAGINATION ── */
function renderPagination() {
  const totalPage = Math.ceil(dataFiltered.length / PER_PAGE) || 1;
  const container = document.getElementById('pagination');
  if (!container) return;

  let html = `<button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>«</button>`;

  for (let i = 1; i <= totalPage; i++) {
    html += `<button class="${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
  }

  html += `<button onclick="changePage(${currentPage + 1})" ${currentPage === totalPage ? 'disabled' : ''}>»</button>`;
  container.innerHTML = html;
}

function changePage(page) {
  const totalPage = Math.ceil(dataFiltered.length / PER_PAGE) || 1;
  if (page < 1 || page > totalPage) return;
  currentPage = page;
  renderTable();
  renderPagination();
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  loadLaporan();

  document.getElementById('search')  ?.addEventListener('input', loadLaporan);
  document.getElementById('btn-cari')?.addEventListener('click', loadLaporan);
});