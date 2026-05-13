// ============================================================
//  dashboard.js — KasirPro | Clean Version
// ============================================================

/* ── HELPERS ── */
function setElText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function formatRupiah(angka) {
  return 'Rp ' + (parseInt(angka, 10) || 0).toLocaleString('id-ID');
}

function showError(id, message) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = message;
  el.classList.add('show-error');
}

function isValidEmail(str) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str);
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(';').shift() : '';
}

/* ── TOAST ── */
function showToast(message, type = 'default') {
  const existing = document.getElementById('toast-notif');
  if (existing) existing.remove();

  const colors = {
    success: '#16a34a',
    danger : '#dc2626',
    warning: '#d97706',
    default: '#333'
  };

  const toast = document.createElement('div');
  toast.id = 'toast-notif';
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: ${colors[type] || colors.default};
    color: #fff;
    padding: 12px 20px;
    border-radius: 8px;
    z-index: 9999;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transition: opacity 0.4s;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

/* ── KALKULATOR ── */
function hitungTotalKalkulator() {
  // ✅ Indentasi konsisten
  const harga  = parseInt(document.getElementById('harga')?.value?.replace(/\./g, ''), 10)  || 0;
  const diskon = parseInt(document.getElementById('diskon')?.value?.replace(/\./g, ''), 10) || 0;
  const jumlah = parseInt(document.getElementById('jumlah')?.value, 10) || 0;

  const totalKotor  = harga * jumlah;
  const nilaiDiskon = Math.min(diskon * jumlah, totalKotor);
  const total       = Math.max(0, totalKotor - nilaiDiskon);

  setElText('total', formatRupiah(total));
}

/* ── SIMPAN DATA ── */
async function hitungDanSimpan() {
  const nama     = document.getElementById('nama')?.value?.trim()                            || '';
  const harga    = parseInt(document.getElementById('harga')?.value?.replace(/\./g, ''), 10) || 0;
  const diskon   = parseInt(document.getElementById('diskon')?.value?.replace(/\./g, ''), 10)|| 0;
  const jumlah   = parseInt(document.getElementById('jumlah')?.value, 10)                    || 0;
  const kategori = document.getElementById('kategori')?.value?.trim()                        || 'Umum';

  if (!nama)        return showToast('Nama barang wajib diisi!', 'warning');
  if (harga === 0)  return showToast('Harga tidak boleh 0!', 'warning');
  if (jumlah === 0) return showToast('Jumlah tidak boleh 0!', 'warning');

  const subtotal    = harga * jumlah;
  const nilaiDiskon = Math.min(diskon * jumlah, subtotal);
  const total       = Math.max(0, subtotal - nilaiDiskon);

  try {
    const res = await fetch('/input-kalkulator-barang/simpan', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ nama, harga, diskon, jumlah, kategori })
    });

    const data = await res.json();

    if (data.success) {
      showToast(`Barang tersimpan: ${nama} (${formatRupiah(total)})`, 'success');
      sessionStorage.setItem('pending_invoice', data.invoice);

      ['nama', 'harga', 'diskon'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });

      const jml = document.getElementById('jumlah');
      if (jml) jml.value = '1';

      hitungTotalKalkulator();
      loadStats();
    } else {
      showToast('Gagal: ' + (data.error || 'Terjadi kesalahan'), 'danger');
    }

  } catch (err) {
    console.error(err);
    showToast('Error koneksi ke server', 'danger');
  }
}

/* ── PEMBAYARAN ── */
function bayarDanCatat() {
  const totalText = document.getElementById('total')?.textContent || 'Rp 0';
  const total     = parseInt(totalText.replace(/[^0-9]/g, ''), 10) || 0;
  const invoice   = sessionStorage.getItem('pending_invoice') || '';

  if (total === 0) {
    showToast('Klik "Hitung dan Simpan" dulu!', 'warning');
    return;
  }

  window.location.href = `/pembayaran?total_harga=${total}&invoice=${invoice}`;
}

/* ── UNDUH LAPORAN ── */
// ✅ Fungsi baru untuk button "Unduh Laporan"
async function unduhLaporan() {
  showToast('Menyiapkan laporan...', 'default');

  try {
    const res = await fetch('/api/laporan/unduh', {
      method : 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!res.ok) throw new Error('Gagal mengunduh laporan');

    // ── Ambil nama file dari header jika ada ──
    const disposition = res.headers.get('Content-Disposition');
    let filename = 'laporan_kasir.pdf';
    if (disposition && disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '').trim();
    }

    // ── Buat link download otomatis ──
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');

    a.href     = url;
    a.download = filename;
    a.click();

    URL.revokeObjectURL(url);
    showToast('Laporan berhasil diunduh!', 'success');

  } catch (err) {
    console.error(err);
    // ── Fallback: redirect ke halaman laporan ──
    showToast('Membuka halaman laporan...', 'default');
    window.location.href = '/laporan';
  }
}

/* ── LOAD STATS ── */
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) throw new Error(res.status);

    const data = await res.json();

    setElText('omzet-hari-ini',    formatRupiah(data.omset_hari_ini));
    setElText('transaksi-hari-ini', data.transaksi_hari_ini ?? 0);
    setElText('barang-terjual',    (data.barang_terjual ?? 0) + ' pcs');

    updateFooterTime();
  } catch (err) {
    console.error('loadStats error:', err);
  }
}

/* ── FOOTER TIME ── */
function updateFooterTime() {
  const now   = new Date();
  const jam   = String(now.getHours()).padStart(2, '0');
  const menit = String(now.getMinutes()).padStart(2, '0');
  setElText('update-time', `${jam}:${menit}`);
}

/* ── RESET DATA ── */
function resetAll() {
  if (!confirm('Reset semua data hari ini?')) return;

  fetch('/api/reset', {
    method : 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken' : getCookie('csrf_token')
    }
  })
    .then(r => {
      if (!r.ok) throw new Error('Gagal reset');
      return r.json();
    })
    .then(d => {
      ['omzet-hari-ini', 'transaksi-hari-ini', 'barang-terjual', 'total']
        .forEach(id => setElText(id, '0'));

      loadStats();
      showToast(d.message || 'Data direset', 'success');
    })
    .catch(err => showToast(err.message, 'danger'));
}

/* ── VALIDASI FIELD ── */
function validateField(input, errorId, message) {
  if (!input) return true;
  const errEl = document.getElementById(errorId);
  const val   = input.value.trim();

  if (!val) {
    input.classList.add('error');
    if (errEl) { errEl.textContent = message; errEl.classList.add('show'); }
    return false;
  }

  if (input.type === 'number' && (isNaN(val) || Number(val) <= 0)) {
    input.classList.add('error');
    if (errEl) { errEl.textContent = 'Harus lebih dari 0'; errEl.classList.add('show'); }
    return false;
  }

  input.classList.remove('error');
  if (errEl) errEl.classList.remove('show');
  return true;
}

function clearOnInput(input, errorId) {
  if (!input) return;
  input.addEventListener('input', function () {
    input.classList.remove('error');
    const errEl = document.getElementById(errorId);
    if (errEl) errEl.classList.remove('show');
  });
}

/* ── FITUR SELECT (MODAL) ── */
function initFiturSelect() {
  const fiturSelect = document.getElementById('fitur');
  if (!fiturSelect) return;

  fiturSelect.addEventListener('change', function () {
    const pilihan = this.value;
    if (pilihan === 'memo')     window.location.href = '/memo';
    if (pilihan === 'kalender') window.location.href = '/kalender';
    if (pilihan === 'jam')      window.location.href = '/jam';
  });
}

/* ── INIT — satu DOMContentLoaded ── */
// ✅ Semua digabung dalam SATU DOMContentLoaded
document.addEventListener('DOMContentLoaded', function () {

  // Kalkulator
  ['harga', 'diskon', 'jumlah'].forEach(id =>
    document.getElementById(id)?.addEventListener('input', hitungTotalKalkulator)
  );

  // Tombol kalkulator
  document.getElementById('btn-hitung-simpan')?.addEventListener('click', hitungDanSimpan);
  document.getElementById('btn-bayar')?.addEventListener('click', bayarDanCatat);

  // ✅ Tombol unduh laporan — bisa pakai addEventListener ATAU onclick di HTML
  document.querySelector('.btn-outline[onclick="unduhLaporan()"]')
    ?.addEventListener('click', unduhLaporan);

  // Validasi form tambah transaksi
  const inputNamaBarang = document.getElementById('nama_barang');
  const inputJumlah     = document.getElementById('jumlah');
  const inputHarga      = document.getElementById('harga');

  clearOnInput(inputNamaBarang, 'err-nama_barang');
  clearOnInput(inputJumlah,     'err-jumlah');
  clearOnInput(inputHarga,      'err-harga');

  // ✅ Placeholder yang benar
  if (inputNamaBarang) inputNamaBarang.placeholder = 'cth: Aqua Botol 600ml';
  if (inputJumlah)     inputJumlah.placeholder     = 'cth: 5';       // ← diperbaiki
  if (inputHarga)      inputHarga.placeholder       = 'cth: 5000';

  // Format harga saat blur
  if (inputHarga) {
    inputHarga.addEventListener('blur', function () {
      const val = parseInt(this.value.replace(/\D/g, ''), 10);
      if (!isNaN(val) && val > 0) {
        this.setAttribute('data-raw', val);
      }
    });
  }

  // Fitur select
  initFiturSelect();

  // Init waktu & stats
  updateFooterTime();
  loadStats();

  setInterval(loadStats,         30000);
  setInterval(updateFooterTime,  60000);
});