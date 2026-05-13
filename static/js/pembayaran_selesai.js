// Contoh fungsi untuk tombol (sesuaikan dengan kebutuhan)
  document.querySelector('.btn-primary-custom').addEventListener('click', function() {
    alert('Fungsi lihat detail transaksi belum diimplementasikan.');
  });

  document.querySelector('.btn-outline-custom').addEventListener('click', function() {
    alert('Fungsi unduh bukti pembayaran belum diimplementasikan.');
  });

  document.querySelector('.btn-ghost-custom').addEventListener('click', function() {
    alert('Fungsi kembali ke beranda belum diimplementasikan.');
  });
  //animansi tombol bisa ditambahkan sesuai kebutuhan
  //animasi tombol
  document.querySelectorAll('.btn-group-custom button').forEach(btn => {
    btn.addEventListener('mouseover', function() {
      this.classList.add('animate-hover');
    });

    btn.addEventListener('mouseout', function() {
      this.classList.remove('animate-hover');
    });
  });

// --- 1. FITUR: TOAST NOTIFICATION ---
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerText = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
// animasi pop up

document.querySelectorAll('.btn-primary-custom').forEach(btn => {
    btn.addEventListener('click', function() {
        showToast('Fungsi lihat detail transaksi belum diimplementasikan.', 'info');
    });
});