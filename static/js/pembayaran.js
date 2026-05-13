// ── DATA BANK ──────────────────────────────────────────────
const BANK_DATA = {
  BCA:     { warna: '#003f88', prefix: '888',  panjang: 10, nama_rekening: 'KasirPro Store' },
  Mandiri: { warna: '#f0a500', prefix: '1070', panjang: 13, nama_rekening: 'KasirPro Store' },
  BNI:     { warna: '#f26522', prefix: '0',    panjang: 10, nama_rekening: 'KasirPro Store' },
  BRI:     { warna: '#003087', prefix: '0096', panjang: 15, nama_rekening: 'KasirPro Store' },
  CIMB:    { warna: '#c00000', prefix: '800',  panjang: 13, nama_rekening: 'KasirPro Store' },
  Permata: { warna: '#6d4c9f', prefix: '8',    panjang: 10, nama_rekening: 'KasirPro Store' }
};

// ── DATA E-WALLET ───────────────────────────────────────────
const WALLET_DATA = {
  GoPay:     { warna: '#00AED6' },
  OVO:       { warna: '#4C3494' },
  DANA:      { warna: '#118EEA' },
  ShopeePay: { warna: '#EE4D2D' },
  LinkAja:   { warna: '#E82529' }
};

// ── HELPERS ────────────────────────────────────────────────
function formatRp(angka) {
  return 'Rp ' + (parseInt(angka) || 0).toLocaleString('id-ID');
}

function getRawNumber(str) {
  return parseInt((str || '').replace(/\D/g, '')) || 0;
}

function formatNoRek(noRek) {
  return noRek.replace(/(\d{4})(?=\d)/g, '$1 ');
}

function getTotal() {
  const el = document.getElementById('total-amount');
  return getRawNumber(el?.textContent || '0');
}

// ── GENERATE NOMOR REKENING TOKO (ACAK) ────────────────────
function generateNoRek(bank) {
  const data = BANK_DATA[bank];
  const sisa = data.panjang - data.prefix.length;
  let acak   = '';
  for (let i = 0; i < sisa; i++) acak += Math.floor(Math.random() * 10);
  return data.prefix + acak;
}

// ── SIMPAN NO REK TUJUAN (TOKO) ────────────────────────────
function simpanNoRek(noRek) {
  let el = document.getElementById('no_rekening_tujuan');
  if (!el) {
    el      = document.createElement('input');
    el.type = 'hidden';
    el.name = 'no_rekening_tujuan';
    el.id   = 'no_rekening_tujuan';
    document.querySelector('form')?.appendChild(el);
  }
  el.value = noRek;
}

// ── SIMPAN NO REK PELANGGAN KE HIDDEN INPUT ─────────────────
function simpanNoRekeningPelanggan(nilai) {
  const el = document.getElementById('no_rekening_hidden');
  if (el) el.value = nilai.replace(/\D/g, '');
}

// ── COPY NOMOR REKENING ─────────────────────────────────────
function copyNoRek(noRek, btn) {
  navigator.clipboard.writeText(noRek).then(() => {
    const ori            = btn.innerHTML;
    btn.innerHTML        = '<i class="fas fa-check"></i> Tersalin!';
    btn.style.background = '#22c55e';
    btn.style.color      = '#fff';
    setTimeout(() => { btn.innerHTML = ori; btn.style.background = ''; btn.style.color = ''; }, 2000);
  }).catch(() => {
    const ori            = btn.innerHTML;
    btn.innerHTML        = 'Gagal';
    btn.style.background = '#ef4444';
    btn.style.color      = '#fff';
    setTimeout(() => { btn.innerHTML = ori; btn.style.background = ''; btn.style.color = ''; }, 1500);
  });
}

// ── TAMPILKAN INFO TRANSFER BANK ────────────────────────────
function tampilkanTransferBank(bank) {
  const data  = BANK_DATA[bank];
  const noRek = generateNoRek(bank);
  const total = document.getElementById('total-amount')?.textContent?.trim() || 'Rp 0';

  simpanNoRek(noRek);

  const panel = document.getElementById('info-transfer-bank');
  if (!panel) return;

  panel.style.display = 'block';
  panel.innerHTML = `
    <div style="border-left:4px solid ${data.warna}; background:#fff; border-radius:10px;
                border:1.5px solid #e9ecef; padding:16px; margin-top:12px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
        <span style="background:${data.warna}; color:${bank==='Mandiri'?'#333':'#fff'};
                     font-weight:700; font-size:13px; padding:4px 12px; border-radius:6px;">
          ${bank.toUpperCase()}
        </span>
        <span style="font-size:13px; color:#6c757d;">Informasi Transfer ke Toko</span>
      </div>
      <div style="display:flex; justify-content:space-between; padding:8px 0; border-top:1px solid #e9ecef; font-size:13px;">
        <span style="color:#6c757d;">Nama Rekening</span>
        <span style="font-weight:600; color:#212529;">${data.nama_rekening}</span>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-top:1px solid #e9ecef; font-size:13px;">
        <span style="color:#6c757d;">Nomor Rekening Toko</span>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:15px; font-weight:700; letter-spacing:2px; color:#212529;">${formatNoRek(noRek)}</span>
          <button type="button" onclick="copyNoRek('${noRek}', this)"
            style="padding:5px 10px; border:1.5px solid #4361ee; border-radius:6px; background:#fff; color:#4361ee; font-size:12px; cursor:pointer;">
            <i class="fas fa-copy"></i> Salin
          </button>
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; padding:8px 0; border-top:1px solid #e9ecef; font-size:13px;">
        <span style="color:#6c757d;">Jumlah Transfer</span>
        <span style="font-weight:700; font-size:15px; color:${data.warna};">${total}</span>
      </div>
      <div style="margin-top:12px; padding:10px 12px; background:#fff8e1; border-radius:8px; font-size:12px; color:#856404; display:flex; gap:8px;">
        <i class="fas fa-exclamation-circle" style="margin-top:1px; flex-shrink:0;"></i>
        Transfer tepat sesuai nominal. Tunjukkan bukti transfer ke kasir.
      </div>
      <button type="button" onclick="pickBank('${bank}', document.querySelector('.bank-btn.picked'))"
        style="margin-top:10px; width:100%; padding:8px; border:1.5px solid #ced4da; border-radius:8px; background:#f8f9fa; font-size:13px; cursor:pointer; color:#212529;">
        <i class="fas fa-sync-alt"></i> Generate Nomor Baru
      </button>
    </div>`;

  const divNoRek = document.getElementById('div-no-rekening-kartu');
  if (divNoRek) divNoRek.style.display = 'block';

  cekBisaProses();
}

// ── TAMPILKAN INFO E-WALLET ─────────────────────────────────
function tampilkanTransferWallet(wallet) {
  const data  = WALLET_DATA[wallet] || { warna: '#4361ee' };
  const total = document.getElementById('total-amount')?.textContent?.trim() || 'Rp 0';

  const panel = document.getElementById('info-transfer-wallet');
  if (!panel) return;

  panel.style.display = 'block';
  panel.innerHTML = `
    <div style="border-left:4px solid ${data.warna}; background:#fff; border-radius:10px;
                border:1.5px solid #e9ecef; padding:16px; margin-top:12px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
        <span style="background:${data.warna}; color:#fff; font-weight:700; font-size:13px; padding:4px 12px; border-radius:6px;">
          ${wallet.toUpperCase()}
        </span>
        <span style="font-size:13px; color:#6c757d;">Pembayaran E-Wallet</span>
      </div>
      <div style="display:flex; justify-content:space-between; padding:8px 0; border-top:1px solid #e9ecef; font-size:13px;">
        <span style="color:#6c757d;">Jumlah Transfer</span>
        <span style="font-weight:700; font-size:15px; color:${data.warna};">${total}</span>
      </div>
      <div style="margin-top:12px; padding:10px 12px; background:#fff8e1; border-radius:8px; font-size:12px; color:#856404; display:flex; gap:8px;">
        <i class="fas fa-exclamation-circle" style="margin-top:1px; flex-shrink:0;"></i>
        Transfer via aplikasi ${wallet}. Tunjukkan bukti ke kasir.
      </div>
    </div>`;

  const divEwallet = document.getElementById('div-no-ewallet');
  if (divEwallet) divEwallet.style.display = 'block';

  cekBisaProses();
}

// ── PILIH METODE ────────────────────────────────────────────
function selectMethod(m, btn) {
  ['tunai', 'kartu', 'ewallet'].forEach(x => {
    document.getElementById('btn-' + x)?.classList.remove('active');
    document.getElementById('panel-' + x)?.classList.remove('open');
  });

  btn.classList.add('active');
  document.getElementById('panel-' + m)?.classList.add('open');
  document.getElementById('payment_method').value = m;

  const label    = m === 'tunai' ? 'Tunai' : m === 'kartu' ? 'Kartu' : 'E-Wallet';
  const elMethod = document.getElementById('summary-method');
  if (elMethod) elMethod.textContent = label;

  const sectionCash = document.getElementById('section-cash');
  const infoBank    = document.getElementById('info-transfer-bank');
  const infoWallet  = document.getElementById('info-transfer-wallet');
  const divNoRek    = document.getElementById('div-no-rekening-kartu');
  const divEwallet  = document.getElementById('div-no-ewallet');

  if (sectionCash) sectionCash.style.display = m === 'tunai' ? 'flex' : 'none';
  if (infoBank)    { infoBank.innerHTML = '';   infoBank.style.display   = 'none'; }
  if (infoWallet)  { infoWallet.innerHTML = ''; infoWallet.style.display = 'none'; }
  if (divNoRek)    divNoRek.style.display   = 'none';
  if (divEwallet)  divEwallet.style.display = 'none';

  const inputRek = document.getElementById('input-no-rekening-kartu');
  const inputEw  = document.getElementById('input-no-rekening-ewallet');
  const hidden   = document.getElementById('no_rekening_hidden');
  if (inputRek) inputRek.value = '';
  if (inputEw)  inputEw.value  = '';
  if (hidden)   hidden.value   = '';

  document.querySelectorAll('.bank-btn, .wallet-btn').forEach(b => b.classList.remove('picked'));
  document.getElementById('no_rekening_tujuan')?.remove();

  if (m === 'tunai') validateCash();
  cekBisaProses();
}

// ── PILIH BANK ──────────────────────────────────────────────
function pickBank(bank, btn) {
  document.querySelectorAll('.bank-btn').forEach(b => b.classList.remove('picked'));
  if (btn) btn.classList.add('picked');

  document.getElementById('payment_method').value = 'kartu_' + bank.toLowerCase();

  const elMethod = document.getElementById('summary-method');
  if (elMethod) elMethod.textContent = 'Kartu — ' + bank;

  const inputRek = document.getElementById('input-no-rekening-kartu');
  if (inputRek) { inputRek.value = ''; simpanNoRekeningPelanggan(''); }

  tampilkanTransferBank(bank);
}

// ── PILIH E-WALLET ──────────────────────────────────────────
function pickWallet(wallet, btn) {
  document.querySelectorAll('.wallet-btn').forEach(b => b.classList.remove('picked'));
  btn.classList.add('picked');

  document.getElementById('payment_method').value = 'ewallet_' + wallet.toLowerCase();

  const elMethod = document.getElementById('summary-method');
  if (elMethod) elMethod.textContent = 'E-Wallet — ' + wallet;

  const inputEw = document.getElementById('input-no-rekening-ewallet');
  if (inputEw) { inputEw.value = ''; simpanNoRekeningPelanggan(''); }

  tampilkanTransferWallet(wallet);
}

// ── VALIDASI UANG TUNAI ─────────────────────────────────────
function validateCash() {
  const method = document.getElementById('payment_method')?.value;
  if (method !== 'tunai') return;

  const TOTAL     = getTotal();
  const cashInput = document.getElementById('cash-amount');
  const raw       = getRawNumber(cashInput?.value || '');
  const kembalian = raw - TOTAL;

  const changeDisplay = document.getElementById('change-display');
  const changeAmt     = document.getElementById('change-amount');
  const summaryBayar  = document.getElementById('summary-bayar-val');
  const summaryKemRow = document.getElementById('summary-kembalian-row');
  const summaryKem    = document.getElementById('summary-kembalian-val');

  if (raw === 0) {
    if (changeDisplay) changeDisplay.className     = 'change-display';
    if (changeAmt)     changeAmt.textContent       = '—';
    if (summaryBayar)  summaryBayar.textContent    = '—';
    if (summaryKemRow) summaryKemRow.style.display = 'none';
    cekBisaProses();
    return;
  }

  if (summaryBayar) summaryBayar.textContent = formatRp(raw);

  if (raw >= TOTAL) {
    if (changeDisplay) changeDisplay.className     = 'change-display valid';
    if (changeAmt)     changeAmt.textContent       = formatRp(kembalian);
    if (summaryKemRow) summaryKemRow.style.display = 'flex';
    if (summaryKem)    summaryKem.textContent      = formatRp(kembalian);
  } else {
    if (changeDisplay) changeDisplay.className     = 'change-display invalid';
    if (changeAmt)     changeAmt.textContent       = '- ' + formatRp(TOTAL - raw) + ' (kurang)';
    if (summaryKemRow) summaryKemRow.style.display = 'none';
  }

  cekBisaProses();
}

// ── CEK BOLEH PROSES ────────────────────────────────────────
function cekBisaProses() {
  const btnProses = document.getElementById('btn-proses');
  if (!btnProses) return;

  const method = document.getElementById('payment_method')?.value || '';
  let boleh    = false;

  if (method === 'tunai') {
    const cash  = getRawNumber(document.getElementById('cash-amount')?.value || '');
    const total = getTotal();
    boleh = cash > 0 && cash >= total;

  } else if (method.includes('kartu')) {
    const bankDipilih = !!document.querySelector('.bank-btn.picked');
    const noRek       = document.getElementById('input-no-rekening-kartu')?.value?.trim() || '';
    boleh = bankDipilih && noRek.length >= 8;

  } else if (method.includes('ewallet')) {
    const walletDipilih = !!document.querySelector('.wallet-btn.picked');
    const noEw          = document.getElementById('input-no-rekening-ewallet')?.value?.trim() || '';
    boleh = walletDipilih && noEw.length >= 8;
  }

  btnProses.disabled = !boleh;
}

// ── QUICK BUTTONS ───────────────────────────────────────────
function initQuickButtons() {
  document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = document.getElementById('cash-amount');
      if (input && this.dataset.amount) {
        input.value = parseInt(this.dataset.amount).toLocaleString('id-ID');
        validateCash();
        input.focus();
      }
    });
  });
}

// ── FORMAT INPUT ANGKA ──────────────────────────────────────
function initFormatInput() {
  const input = document.getElementById('cash-amount');
  if (!input) return;
  input.addEventListener('input', function () {
    const raw  = this.value.replace(/\D/g, '');
    const prev = this.value.length;
    this.value = raw ? parseInt(raw).toLocaleString('id-ID') : '';
    const diff = this.value.length - prev;
    try { const pos = this.selectionStart + diff; this.setSelectionRange(pos, pos); } catch (_) {}
    validateCash();
  });
}

// ── RESET ───────────────────────────────────────────────────
function initReset() {
  document.getElementById('btn-reset')?.addEventListener('click', function () {
    const cashInput = document.getElementById('cash-amount');
    if (cashInput) cashInput.value = '';

    const inputRek = document.getElementById('input-no-rekening-kartu');
    const inputEw  = document.getElementById('input-no-rekening-ewallet');
    const hidden   = document.getElementById('no_rekening_hidden');
    if (inputRek) inputRek.value = '';
    if (inputEw)  inputEw.value  = '';
    if (hidden)   hidden.value   = '';

    document.querySelectorAll('.bank-btn, .wallet-btn').forEach(b => b.classList.remove('picked'));
    document.getElementById('no_rekening_tujuan')?.remove();

    const infoBank   = document.getElementById('info-transfer-bank');
    const infoWallet = document.getElementById('info-transfer-wallet');
    const divNoRek   = document.getElementById('div-no-rekening-kartu');
    const divEwallet = document.getElementById('div-no-ewallet');
    if (infoBank)    { infoBank.innerHTML   = ''; infoBank.style.display   = 'none'; }
    if (infoWallet)  { infoWallet.innerHTML = ''; infoWallet.style.display = 'none'; }
    if (divNoRek)    divNoRek.style.display   = 'none';
    if (divEwallet)  divEwallet.style.display = 'none';

    selectMethod('tunai', document.getElementById('btn-tunai'));
    cashInput?.focus();
  });
}

// ── PROSES PEMBAYARAN (dengan loading overlay) ──────────────
function prosesPayment() {
  // Tampilkan loading overlay
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.style.display = 'flex';
  }

  // Disable tombol cegah double klik
  const btnProses = document.getElementById('btn-proses');
  if (btnProses) btnProses.disabled = true;

  // Submit form ke Flask setelah 1.5 detik
  setTimeout(function () {
    document.getElementById('paymentForm').submit();
  }, 1500);
}

// ── INIT ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initQuickButtons();
  initFormatInput();
  initReset();

  document.getElementById('panel-tunai')?.classList.add('open');
  document.getElementById('btn-tunai')?.classList.add('active');

  cekBisaProses();
});