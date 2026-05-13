/**
 * MODUL: DETAIL TRANSAKSI - KASIRPRO
 */

// --- 1. HELPER: NOTIFIKASI TOAST ---
function showToast(message, type = 'success') {
    const existing = document.getElementById('toast-notif');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'toast-notif';
    toast.textContent = message;

    const bgColor = type === 'success' ? '#1D9E75' : '#E24B4A';
    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px;
        background: ${bgColor}; color: #fff; padding: 12px 20px;
        border-radius: 8px; font-size: 14px; font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999; opacity: 0; transition: opacity 0.3s ease;
    `;

    document.body.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = '1'; });

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --- 2. FITUR: SEARCH ITEM DALAM TABEL ---
function initSearchTransaksi() {
    const searchInput = document.getElementById('searchItemInput');
    const noResult = document.getElementById('no-result-message');
    if (!searchInput) return;

    searchInput.addEventListener('input', function () {
        const searchTerm = this.value.trim().toLowerCase();
        const rows = document.querySelectorAll('.items-table tbody tr:not(.empty-row)');
        let visibleCount = 0;

        rows.forEach(row => {
            const namaItem = row.querySelector('.item-name')?.textContent.toLowerCase() || '';
            const isVisible = namaItem.includes(searchTerm);
            row.style.display = isVisible ? 'table-row' : 'none';
            if (isVisible) visibleCount++;
        });

        if (noResult) {
            noResult.style.display = (visibleCount === 0 && searchTerm !== '') ? 'block' : 'none';
        }
    });
}

// --- 3. FITUR: COPY TO CLIPBOARD ---
function initCopyInvoice() {
    const invoiceEl = document.getElementById('invoiceNumber');
    if (!invoiceEl) return;

    invoiceEl.style.cursor = 'pointer';
    invoiceEl.title = 'Klik untuk menyalin nomor invoice';

    invoiceEl.addEventListener('click', function () {
        const text = this.innerText.trim();
        navigator.clipboard.writeText(text).then(() => {
            showToast('Invoice ' + text + ' berhasil disalin!');
        }).catch(() => {
            showToast('Gagal menyalin invoice', 'error');
        });
    });
}

// --- 4. FITUR: EXPORT HANDLER (PDF/EMAIL) ---
async function handleExport(type, btn) {
    const transactionId = btn.getAttribute('data-id');
    const originalContent = btn.innerHTML;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';

    const endpoints = {
        'pdf': `/transaksi/unduh_pdf/${transactionId}`,
        'email': `/transaksi/kirim_email/${transactionId}`
    };

    try {
        const response = await fetch(endpoints[type]);
        if (!response.ok) throw new Error('Terjadi kesalahan pada server.');

        if (type === 'pdf') {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Invoice_${transactionId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            showToast('PDF berhasil diunduh');
        } else {
            const result = await response.json();
            showToast(result.message || 'Email berhasil dikirim');
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalContent;
    }
}

// --- 5. FITUR: COUNTDOWN TIMER BATALKAN ---
function initCountdownBatalkan() {
    const countdownEl = document.getElementById('countdown-batalkan');
    const btnBatalkan = document.getElementById('btn-batalkan');
    if (!countdownEl || !btnBatalkan) return;

    let sisaDetik = parseInt(countdownEl.getAttribute('data-sisa-detik')) || 0;

    if (sisaDetik <= 0) {
        countdownEl.textContent = 'Waktu habis';
        btnBatalkan.disabled = true;
        return;
    }

    const interval = setInterval(() => {
        sisaDetik--;

        const menit = Math.floor(sisaDetik / 60).toString().padStart(2, '0');
        const detik = (sisaDetik % 60).toString().padStart(2, '0');
        countdownEl.textContent = `${menit}:${detik}`;

        if (sisaDetik <= 60) {
            countdownEl.style.color = '#E24B4A';
            countdownEl.style.fontWeight = 'bold';
        }

        if (sisaDetik <= 0) {
            clearInterval(interval);
            countdownEl.textContent = 'Waktu habis';
            btnBatalkan.disabled = true;
            showToast('Waktu pembatalan telah habis.', 'error');
        }
    }, 1000);
}

// --- 6. INITIALIZER (SATU, LENGKAP) ---
document.addEventListener('DOMContentLoaded', () => {
    initSearchTransaksi();
    initCopyInvoice();
    initCountdownBatalkan();
});