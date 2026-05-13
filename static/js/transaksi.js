document.addEventListener('DOMContentLoaded', () => {

  // =============================================
  // 1. LIVE SEARCH - Filter tabel secara real-time
  // =============================================
  const inputClear = document.getElementById('inputClear');
  const btnClear   = document.getElementById('btnClear');
  const rows       = document.querySelectorAll('table tbody tr');
  const noResult   = document.getElementById('noResult');

  function filterTable() {
    const keyword = inputClear.value.toLowerCase().trim();

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(keyword) ? '' : 'none';
    });

    // Tampilkan pesan jika tidak ada hasil
    if (noResult) {
      const visible = [...rows].some(r => r.style.display !== 'none');
      noResult.style.display = visible ? 'none' : '';
    }
  }

  // Tombol clear (×)
  if (inputClear && btnClear) {
    inputClear.addEventListener('input', () => {
      btnClear.style.display = inputClear.value ? 'block' : 'none';
      filterTable();
    });

    btnClear.addEventListener('click', () => {
      inputClear.value = '';
      btnClear.style.display = 'none';
      filterTable();
    });
  }


  // =============================================
  // 2. TOMBOL CARI & ENTER KEY
  // =============================================
  const btnSearch = document.querySelector('.btn-primary[type="button"]');
  if (btnSearch) {
    btnSearch.addEventListener('click', filterTable);
  }

  if (inputClear) {
    inputClear.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') filterTable();
    });
  }


  // =============================================
  // 3. FORMAT RUPIAH - Kolom Total (kolom ke-4)
  // =============================================
  document.querySelectorAll('table tbody tr td:nth-child(4)').forEach(td => {
    const raw = td.innerText.replace(/[^0-9]/g, '');
    if (raw) {
      td.innerText = 'Rp' + parseInt(raw).toLocaleString('id-ID');
    }
  });


  // =============================================
  // 4. SORT TABEL - Klik header untuk urutkan
  // =============================================
  document.querySelectorAll('table thead th').forEach((th, index) => {
    th.style.cursor = 'pointer';
    th.dataset.order = 'asc';

    th.addEventListener('click', function () {
      const tbody = document.querySelector('table tbody');
      const rowList = [...tbody.querySelectorAll('tr')];
      const order = this.dataset.order;

      rowList.sort((a, b) => {
        const aVal = a.cells[index]?.innerText.toLowerCase() ?? '';
        const bVal = b.cells[index]?.innerText.toLowerCase() ?? '';
        return order === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      });

      this.dataset.order = order === 'asc' ? 'desc' : 'asc';
      rowList.forEach(row => tbody.appendChild(row));
    });
  });


  // =============================================
  // 5. KONFIRMASI HAPUS - Tombol danger
  // =============================================
  document.querySelectorAll('.btn-danger').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (!confirm('Apakah Anda yakin ingin menghapus item ini?')) {
        e.preventDefault();
      }
    });
  });


  // =============================================
  // 6. MODAL SUKSES
  // =============================================
  const modalSukses  = document.getElementById('modal-sukses');
  const btnModalClose = document.getElementById('btn-modal-close');

  if (modalSukses && btnModalClose) {
    btnModalClose.addEventListener('click', () => {
      modalSukses.classList.remove('show');
    });
  }

}); // END DOMContentLoaded