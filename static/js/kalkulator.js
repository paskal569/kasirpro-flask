/* ═══════════════════════════════════════════════════════════
   KALKULATOR KASIR — kalkulator.js
   ═══════════════════════════════════════════════════════════

   ALUR PENGGUNAAN:
   1. Ketik nominal → tekan "Set Total Belanja"
   2. Ketik nominal bayar → tekan "Set Bayar"
      → Jumlah Bayar & Kembalian akan tampil
   3. Kalau sudah lunas → tombol "Masukkan Ke Pendapatan" aktif

   KONVENSI SATUAN:
   • Display  : angka "ribuan" mentah, contoh "25" berarti Rp 25.000
   • Variabel internal disimpan dalam RUPIAH PENUH (sudah × 1000)
   • Konversi : rupiah = displayAngka × 1_000
   ═══════════════════════════════════════════════════════════ */

// ── Konstanta ──────────────────────────────────────────────
var MULTIPLIER = 1000; // 1 satuan display = Rp 1.000

// ── State ──────────────────────────────────────────────────
var totalBelanja  = 0;
var jumlahBayar   = 0;
var sudahSetBayar = false;

// ── Utilitas ───────────────────────────────────────────────

/** Format angka menjadi string Rupiah. Contoh: 25000 → "25.000" */
function formatRupiah(num) {
  if (isNaN(num) || num === null) return '0';
  return Math.round(parseFloat(num))
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

/** Tampilkan string ke layar kalkulator. */
function updateDisplay(value) {
  $('#display-value').text(value);
}

/** Cek apakah string adalah ekspresi yang siap di-eval. */
function isEkspresiSelesai(str) {
  if (!str || str === 'Error') return false;
  if (/[+\-*/.]$/.test(str)) return false;
  if (/[^0-9+\-*/.()]/.test(str)) return false;
  return true;
}

/** Eval ekspresi display → nilai numerik satuan DISPLAY. Null bila gagal. */
function evalDisplay() {
  var ekspresi = $('#display-value').text();
  if (!isEkspresiSelesai(ekspresi)) return null;
  try {
    /* eslint-disable no-eval */
    var hasil = eval(ekspresi);
    /* eslint-enable no-eval */
    if (typeof hasil !== 'number' || !isFinite(hasil) || hasil < 0) return null;
    return hasil;
  } catch (e) {
    return null;
  }
}

// ── Update status tombol ───────────────────────────────────

/**
 * Atur aktif/nonaktif tombol berdasarkan state saat ini.
 * - "Set Bayar"              : aktif hanya jika totalBelanja sudah di-set
 * - "Masukkan Ke Pendapatan" : aktif hanya jika sudah bayar & jumlah cukup
 */
function updateButtons() {
  // Tombol Set Bayar
  if (totalBelanja > 0) {
    $('#btn-set-bayar').prop('disabled', false).css('opacity', '1');
  } else {
    $('#btn-set-bayar').prop('disabled', true).css('opacity', '0.5');
  }

  // Tombol Masukkan Ke Pendapatan
  var bisaSimpan = sudahSetBayar && jumlahBayar > 0 && jumlahBayar >= totalBelanja && totalBelanja > 0;
  if (bisaSimpan) {
    $('#btn-pendapatan').prop('disabled', false).css('opacity', '1');
  } else {
    $('#btn-pendapatan').prop('disabled', true).css('opacity', '0.5');
  }
}

// ── Render ringkasan ───────────────────────────────────────

/** Perbarui tiga baris ringkasan (Total, Bayar, Kembalian) dari state. */
function renderSummary() {
  // Total Belanja
  $('#total-belanja').text('Rp ' + formatRupiah(totalBelanja));

  // Jumlah Bayar
  if (sudahSetBayar && jumlahBayar > 0) {
    $('#jumlah-bayar').text('Rp ' + formatRupiah(jumlahBayar));
  } else {
    $('#jumlah-bayar').text('Rp 0');
  }

  // Kembalian — hanya tampil jika sudah set bayar
  if (!sudahSetBayar || jumlahBayar === 0) {
    $('#kembalian').text('Rp 0').css('color', '');
  } else {
    var kembalian = jumlahBayar - totalBelanja;
    $('#kembalian')
      .text(
        kembalian >= 0
          ? 'Rp ' + formatRupiah(kembalian)
          : '-Rp ' + formatRupiah(Math.abs(kembalian))
      )
      .css('color', kembalian < 0 ? '#f87171' : '#4ade80');
  }

  // Update status tombol setiap kali summary dirender
  updateButtons();
}

// ── Setter state ───────────────────────────────────────────

/** Atur total belanja (Rupiah penuh) dan reset state bayar. */
function setTotalBelanja(rupiah) {
  totalBelanja  = Math.round(rupiah);
  jumlahBayar   = 0;
  sudahSetBayar = false;
  renderSummary();
}

/** Atur jumlah bayar (Rupiah penuh). */
function setJumlahBayar(rupiah) {
  jumlahBayar   = Math.round(rupiah);
  sudahSetBayar = true;
  renderSummary();
}

// ── Hitung ekspresi (tombol =) ─────────────────────────────
function hitungEkspresi() {
  var hasil = evalDisplay();
  if (hasil === null) {
    updateDisplay('Error');
    return;
  }
  updateDisplay(parseFloat(hasil.toFixed(6)).toString());
}

// ── Reset ──────────────────────────────────────────────────
function resetSemua() {
  totalBelanja  = 0;
  jumlahBayar   = 0;
  sudahSetBayar = false;
  updateDisplay('0');
  renderSummary();
}

// ══════════════════════════════════════════════════════════
//  INIT — setelah DOM siap
// ══════════════════════════════════════════════════════════
$(function () {

  // Tampilan awal
  updateDisplay('0');
  renderSummary(); // ini juga memanggil updateButtons()

  // ── Numpad ────────────────────────────────────────────
  $('.numpad button').on('click', function () {
    var tekan   = $(this).data('value').toString();
    var current = $('#display-value').text();

    if (current === 'Error') { current = '0'; }
    if (tekan === '=') { hitungEkspresi(); return; }

    var isOperator = ['+', '-', '*', '/'].includes(tekan);
    var lastChar   = current.slice(-1);

    if (tekan === '.') {
      var segmenTerakhir = current.split(/[+\-*/]/).pop();
      if (segmenTerakhir.includes('.')) return;
    }

    if (isOperator && ['+', '-', '*', '/'].includes(lastChar)) {
      updateDisplay(current.slice(0, -1) + tekan);
      return;
    }

    if (tekan === '00') {
      if (current === '0') return;
      if (['+', '-', '*', '/'].includes(lastChar)) return;
    }

    if (current === '0' && !isOperator && tekan !== '.') {
      updateDisplay(tekan);
    } else {
      updateDisplay(current + tekan);
    }
  });

  // ── Hapus (backspace) ─────────────────────────────────
  $('#btn-hapus').on('click', function () {
    var current = $('#display-value').text();
    if (current === 'Error') { updateDisplay('0'); return; }
    var baru = current.slice(0, -1);
    updateDisplay(baru === '' ? '0' : baru);
  });

  // ── Reset Semua ───────────────────────────────────────
  $('#btn-reset').on('click', function () {
    resetSemua();
  });

  // ── Set Total Belanja ─────────────────────────────────
  $('#btn-set-total-pendapatan').on('click', function () {
    var hasil = evalDisplay();
    if (hasil === null) {
      alert('Masukkan nominal total belanja yang valid terlebih dahulu.');
      updateDisplay('Error');
      return;
    }
    var rupiahPenuh = hasil * MULTIPLIER;
    setTotalBelanja(rupiahPenuh);
    alert('Total belanja diatur: Rp ' + formatRupiah(rupiahPenuh));
    updateDisplay('0');
  });

  // ── Set Jumlah Bayar ──────────────────────────────────
  $('#btn-set-bayar').on('click', function () {
    if (totalBelanja === 0) {
      alert('Set total belanja terlebih dahulu.');
      return;
    }

    var hasil = evalDisplay();
    if (hasil === null) {
      alert('Masukkan nominal bayar yang valid terlebih dahulu.');
      return;
    }

    var rupiahPenuh = hasil * MULTIPLIER;

    // Boleh input berapapun — tampilkan kembalian (bisa negatif jika kurang)
    // Tombol "Masukkan Ke Pendapatan" akan otomatis nonaktif jika kurang bayar
    setJumlahBayar(rupiahPenuh);

    sessionStorage.setItem('kalkulator_total', totalBelanja);
    sessionStorage.setItem('kalkulator_bayar', rupiahPenuh);
    sessionStorage.setItem('kalkulator_kembalian', rupiahPenuh - totalBelanja);

    window.location.href = '/pembayaran/?total_harga=' + totalBelanja;
  });

  // ── Simpan Ke Pendapatan ──────────────────────────────
  $('#btn-pendapatan').on('click', function (e) {
    e.preventDefault();

    if (totalBelanja === 0) {
      alert('Set total belanja terlebih dahulu.');
      return;
    }
    if (!sudahSetBayar || jumlahBayar === 0) {
      alert('Konfirmasi jumlah bayar terlebih dahulu (tekan "Set Bayar").');
      return;
    }
    if (jumlahBayar < totalBelanja) {
      alert(
        'Pembayaran belum lunas.\n' +
        'Kurang: Rp ' + formatRupiah(totalBelanja - jumlahBayar)
      );
      return;
    }

    var namaBarang = $('#nama-barang').val().trim();
    if (!namaBarang) {
      alert('Nama barang wajib diisi sebelum menyimpan transaksi.');
      $('#nama-barang').focus();
      return;
    }
    var kembalian  = jumlahBayar - totalBelanja;

    $.ajax({
      url        : '/api/bayar',
      method     : 'POST',
      contentType: 'application/json',
      data       : JSON.stringify({
        nama_barang  : namaBarang,
        total_harga  : totalBelanja,
        jumlah_bayar : jumlahBayar,
        kembalian    : kembalian,
        jumlah_barang : parseInt($('#jumlah-barang').val()) || 1

      }),
      success: function (res) {
        alert(
          '✅ Transaksi berhasil!\n' +
          'Kembalian: Rp ' + formatRupiah(res.kembalian ?? kembalian)
        );
        $('#nama-barang').val('');
        resetSemua();
      },
      error: function (xhr) {
        var pesan = (xhr.responseJSON && xhr.responseJSON.message)
                    ? xhr.responseJSON.message
                    : 'Terjadi kesalahan pada server.';
        alert('❌ Gagal menyimpan transaksi:\n' + pesan);
      }
    });
  });

}); // ← tutup $(function())

// ── Keyboard Support ──────────────────────────────────────
$(document).on('keydown', function (e) {
  var key = e.key;
  var tag = document.activeElement?.tagName;

  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

  if (/^[0-9]$/.test(key)) {
    $('.numpad button[data-value="' + key + '"]').trigger('click');
  } else if (['+', '-', '*', '/'].includes(key)) {
    $('.numpad button[data-value="' + key + '"]').trigger('click');
  } else if (key === '.') {
    $('.numpad button[data-value="."]').trigger('click');
  } else if (key === 'Enter' || key === '=') {
    e.preventDefault();
    hitungEkspresi();
  } else if (key === 'Backspace') {
    $('#btn-hapus').trigger('click');
  } else if (key === 'Escape' || key === 'Delete') {
    resetSemua();
  }
});