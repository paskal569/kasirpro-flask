
    const searchInput    = document.getElementById('searchInput');
    const filterKategori = document.getElementById('filterKategori');
    const tableRows      = document.querySelectorAll('#tabelBarang tbody tr[data-nama]');

    function filterTable() {
      const query    = searchInput.value.toLowerCase();
      const kategori = filterKategori.value;
      tableRows.forEach(row => {
        const namaOk = row.dataset.nama.includes(query);
        // ✅ FIXED: bandingkan string bukan id
        const katOk  = !kategori || row.dataset.kategori === kategori;
        row.style.display = (namaOk && katOk) ? '' : 'none';
      });
    }

    searchInput.addEventListener('input', filterTable);
    filterKategori.addEventListener('change', filterTable);

    const overlay   = document.getElementById('modalOverlay');
    const card      = document.getElementById('modalCard');
    const form      = document.getElementById('editForm');
    const inputNama = document.getElementById('inputNama');
    const inputStok = document.getElementById('inputStok');

    document.querySelectorAll('.btn-open-modal').forEach(btn => {
      btn.addEventListener('click', () => {
        const id   = btn.dataset.id;
        const nama = btn.dataset.nama;
        const stok = btn.dataset.stok;

        inputNama.value = nama;
        inputStok.value = stok;

        // ✅ FIXED: sesuaikan dengan route edit di stock blueprint
        form.action = `/stock/edit/${id}`;

        openModal();
      });
    });

    function openModal() {
      overlay.classList.add('is-open');
      setTimeout(() => inputNama.focus(), 320);
    }

    function closeModal() {
      overlay.classList.remove('is-open');
      clearErrors();
    }

    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal();
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeModal();
    });

    document.getElementById('btnClose').addEventListener('click', closeModal);
    document.getElementById('btnBatal').addEventListener('click', closeModal);

    form.addEventListener('submit', e => {
      clearErrors();
      let valid = true;

      if (!inputNama.value.trim()) {
        inputNama.classList.add('is-error');
        valid = false;
      }
      if (inputStok.value === '') {
        inputStok.classList.add('is-error');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
        card.classList.remove('shake');
        void card.offsetWidth;
        card.classList.add('shake');
      }
    });

    function clearErrors() {
      document.querySelectorAll('.form-input.is-error')
        .forEach(el => el.classList.remove('is-error'));
    }

  document.getElementById('btnSimpan').addEventListener('click', () => {
  const namaBarang = document.getElementById('nama-barang').value;
  const hargaBeli = document.getElementById('harga-beli').value;
  const hargaJual = document.getElementById('harga-jual').value;
  const stok = document.getElementById('stok').value;

  if (namaBarang.trim() === '' || hargaBeli.trim() === '' || hargaJual.trim() === '' || stok.trim() === '') {
    alert('Mohon isi semua form terlebih dahulu!');
    return;
  }

  const dataBarang = {
    namaBarang,
    hargaBeli,
    hargaJual,
    stok
  };

  const dataBarangJSON = JSON.stringify(dataBarang);

  localStorage.setItem('barangDraft', dataBarangJSON);
  alert('Data berhasil disimpan!');
});