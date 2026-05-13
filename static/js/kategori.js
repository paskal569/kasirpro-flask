 /**
 * kategori-table.js
 * Filter tabel kategori: search real-time + chip filter + shortcut keyboard
 * -------------------------------------------------------------------------
 * Perbaikan dari versi sebelumnya:
 *  - Perbaiki bracket yang salah/tertanam (tambahKategori ⊃ logoutModal)
 *  - Pisahkan setiap fungsi agar mudah di-maintain
 *  - Tambahkan debounce pada input search (performa)
 *  - Tambahkan highlight teks yang cocok saat search
 *  - Tambahkan pesan "tidak ada data" saat filter kosong
 *  - Tambahkan tombol reset search (×) secara dinamis
 *  - Gunakan const/let secara konsisten
 *  - Semua query selector disimpan di variabel (tidak duplikasi)
 */

'use strict';

/* ─── 1. ELEMENT REFERENCES ─────────────────────────────────────────────── */
const searchInput = document.getElementById('searchInput');
const chipGroup   = document.getElementById('chipGroup');
const tableBody   = document.querySelector('#kategoriTable tbody');
const tableRows   = tableBody ? Array.from(tableBody.querySelectorAll('tr')) : [];

/* ─── 2. EMPTY STATE ─────────────────────────────────────────────────────── */
const emptyRow = (() => {
  const colCount = tableRows[0]?.cells.length ?? 5;
  const tr = document.createElement('tr');
  tr.id = 'emptyRow';
  tr.style.display = 'none';
  tr.innerHTML = `
    <td colspan="${colCount}" class="text-center text-muted py-4">
      <i class="bi bi-inbox fs-3 d-block mb-1"></i>
      Tidak ada data yang cocok
    </td>`;
  tableBody?.appendChild(tr);
  return tr;
})();

/* ─── 3. DEBOUNCE HELPER ─────────────────────────────────────────────────── */
function debounce(fn, delay = 200) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/* ─── 4. HIGHLIGHT HELPER ───────────────────────────────────────────────── */
function highlightCell(cell, query) {
  cell.innerHTML = cell.textContent;
  if (!query) return;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex   = new RegExp(`(${escaped})`, 'gi');
  cell.innerHTML = cell.textContent.replace(regex, '<mark>$1</mark>');
}

/* ─── 5. CORE FILTER FUNCTION ───────────────────────────────────────────── */
function filterTable() {
  const query  = searchInput.value.trim().toLowerCase();
  const filter = chipGroup?.querySelector('.chip.active')?.dataset.filter ?? 'semua';
  let visibleCount = 0;

  tableRows.forEach(row => {
    const matchSearch = row.textContent.toLowerCase().includes(query);
    const matchFilter = filter === 'semua' || row.dataset.status === filter;
    const visible     = matchSearch && matchFilter;

    row.style.display = visible ? '' : 'none';

    if (visible) {
      visibleCount++;
      const firstCell = row.querySelector('td:first-child');
      if (firstCell) highlightCell(firstCell, query);
    }
  });

  emptyRow.style.display = visibleCount === 0 ? '' : 'none';
  updateClearButton(query);
}

/* ─── 6. CLEAR BUTTON (×) ───────────────────────────────────────────────── */
const clearBtn = (() => {
  const btn = document.createElement('button');
  btn.type      = 'button';
  btn.className = 'btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y pe-2 text-muted d-none';
  btn.innerHTML = '<i class="bi bi-x-lg"></i>';
  btn.title     = 'Hapus pencarian';
  btn.setAttribute('aria-label', 'Hapus pencarian');

  if (searchInput?.parentElement) {
    searchInput.parentElement.style.position = 'relative';
    searchInput.parentElement.appendChild(btn);
    searchInput.style.paddingRight = '2rem';
  }

  btn.addEventListener('click', () => {
    searchInput.value = '';
    searchInput.focus();
    filterTable();
  });

  return btn;
})();

function updateClearButton(query) {
  clearBtn?.classList.toggle('d-none', !query);
}

/* ─── 7. NAVIGASI & MODAL ────────────────────────────────────────────────── */
function tambahKategori() {
  window.location.href = '/kategori/tambah';
}

function logoutModal() {
  const el = document.getElementById('logoutModal');
  if (!el) {
    console.warn('logoutModal: elemen #logoutModal tidak ditemukan.');
    return;
  }
  new bootstrap.Modal(el).show();
}

/* ─── 8. INISIALISASI (semua dalam DOMContentLoaded) ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

  // Event listener search — hanya SATU kali, dengan debounce
  searchInput?.addEventListener('input', debounce(() => {
    updateClearButton(searchInput.value);
    filterTable();
  }, 200));

  // Shortcut keyboard
  document.addEventListener('keydown', e => {
    const tag = document.activeElement?.tagName;
    if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT') {
      e.preventDefault();
      searchInput?.focus();
    }
    if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.value = '';
      filterTable();
    }
  });

  // Chip filter
  chipGroup?.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chipGroup.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      filterTable();
    });
  });

  // Jalankan filter & clear button saat pertama load
  updateClearButton(searchInput?.value ?? '');
  filterTable();
  searchInput?.focus();
});
//table
//tabel kategori
const tableKategori = document.getElementById('categoryTable');
if (tableKategori) {
  new DataTable(tableKategori, {
    language: {
      searchPlaceholder: 'Cari kategori',
    },
    search: {
      smart: false,
    },
    order: [[1, 'asc']],
    columnDefs: [
      { targets: 0, orderable: false },
      { targets: 1, orderable: false },
      { targets: 2, orderable: false },
      { targets: 3, orderable: false },
    ],
  });
}
/* ── Chip Filter ── */
    document.querySelectorAll('#chipGroup .chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('#chipGroup .chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const filter = chip.dataset.filter;
        document.querySelectorAll('#kategoriTable tbody tr').forEach(row => {
          row.style.display = (filter === 'semua' || row.dataset.status === filter) ? '' : 'none';
        });
      });
    });

    /* ── Search ── */
    document.getElementById('searchInput').addEventListener('input', function() {
      const q = this.value.toLowerCase();
      document.querySelectorAll('#kategoriTable tbody tr').forEach(row => {
        const name = row.querySelector('.cat-name')?.textContent.toLowerCase() || '';
        row.style.display = name.includes(q) ? '' : 'none';
      });
    });
    
     document.getElementById('searchInput').addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('#kategoriTable tbody tr[data-nama]').forEach(row => {
        row.style.display = row.dataset.nama.includes(q) ? '' : 'none';
      });
    });

    // Chip filter
    document.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', function () {
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        this.classList.add('active');
        const filter = this.dataset.filter;
        document.querySelectorAll('#kategoriTable tbody tr[data-status]').forEach(row => {
          row.style.display = (filter === 'semua' || row.dataset.status === filter) ? '' : 'none';
        });
      });
    });

    // Auto-dismiss flash toast setelah 4 detik
    setTimeout(() => {
      document.querySelectorAll('.toast-container .toast').forEach(el => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
      });
    }, 4000);


    (function () {
      const searchInput  = document.getElementById('searchInput');
      const chipGroup    = document.getElementById('chipGroup');
      const tableBody    = document.querySelector('#kategoriTable tbody');
      const noResultMsg  = document.getElementById('noResultMsg');
      const jumlahLabel  = document.getElementById('jumlahLabel');

      let activeFilter = 'semua'; // state filter chip aktif

      // ── Fungsi utama: filter + search ──────────────────────────────
      function applyFilter() {
        const keyword = searchInput.value.trim().toLowerCase();
        const rows    = tableBody.querySelectorAll('tr[data-nama]');
        let visible   = 0;

        rows.forEach(function (row) {
          const nama   = row.getAttribute('data-nama') || '';
          const status = row.getAttribute('data-status') || '';

          const cocokSearch = nama.includes(keyword);
          const cocokChip   = activeFilter === 'semua' || status === activeFilter;

          if (cocokSearch && cocokChip) {
            row.style.display = '';
            visible++;
          } else {
            row.style.display = 'none';
          }
        });

        // Update label jumlah
        jumlahLabel.textContent = visible + ' kategori';

        // Tampilkan pesan kosong jika tidak ada hasil
        noResultMsg.style.display = visible === 0 ? 'block' : 'none';
      }

      // ── Event: ketik di search ──────────────────────────────────────
      searchInput.addEventListener('input', applyFilter);

      // ── Event: klik chip filter ─────────────────────────────────────
      chipGroup.addEventListener('click', function (e) {
        const chip = e.target.closest('.chip');
        if (!chip) return;

        // Update active chip
        chipGroup.querySelectorAll('.chip').forEach(function (c) {
          c.classList.remove('active');
        });
        chip.classList.add('active');

        activeFilter = chip.getAttribute('data-filter');
        applyFilter();
      });
    })();
  