// ==================== IIFE VALIDASI (hanya satu, tidak duplikat) ====================
(function () {
    const form = document.querySelector('form');
    if (!form) return;

    // ✅ Sesuaikan id dengan yang ada di HTML
    const fields = [
        { id: 'nama-barang', label: 'Nama barang' },
        { id: 'harga-beli',  label: 'Harga beli'  },
        { id: 'harga-jual',  label: 'Harga jual'  },
        { id: 'stok',        label: 'Stok'         }
    ];

    function setError(id, message) {
        const input = document.getElementById(id);
        const error = document.getElementById(`${id}-error`);
        if (!input || !error) return;
        error.textContent = message || '';
        input.classList.toggle('is-invalid', Boolean(message));
    }

    function validateField(id, label) {
        const input = document.getElementById(id);
        if (!input) return true;

        if (!input.value.trim()) {
            setError(id, `${label} wajib diisi.`);
            return false;
        }
        if (input.type === 'number' && Number(input.value) < 0) {
            setError(id, `${label} tidak boleh negatif.`);
            return false;
        }
        setError(id, '');
        return true;
    }

    // ✅ Bug 3 diperbaiki — tambah validasi harga jual > harga beli
    function validateHarga() {
        const inputBeli = document.getElementById('harga-beli');
        const inputJual = document.getElementById('harga-jual');
        if (!inputBeli || !inputJual) return true;

        // ✅ Bug format angka — bersihkan titik pemisah ribuan sebelum compare
        const hargaBeli = parseInt(inputBeli.value.replace(/\./g, '')) || 0;
        const hargaJual = parseInt(inputJual.value.replace(/\./g, '')) || 0;

        if (hargaJual <= hargaBeli) {
            setError('harga-jual', 'Harga jual harus lebih besar dari harga beli.');
            return false;
        }
        setError('harga-jual', '');
        return true;
    }

    form.addEventListener('submit', function (event) {
        let isValid = true;
        fields.forEach(({ id, label }) => {
            if (!validateField(id, label)) isValid = false;
        });
        if (!validateHarga()) isValid = false;
        if (!isValid) event.preventDefault();
    });

    fields.forEach(({ id, label }) => {
        const input = document.getElementById(id);
        if (!input) return;
        input.addEventListener('input', () => validateField(id, label));
    });

    // ✅ Bug 4 diperbaiki — null check sebelum addEventListener
    const fileInput  = document.getElementById('gambar');
    const preview    = document.getElementById('gambar-preview');
    const previewImg = document.getElementById('gambar-preview-img');

    if (fileInput && preview && previewImg) {
        fileInput.addEventListener('change', function () {
            const file = this.files && this.files[0];
            if (!file) {
                preview.hidden = true;
                previewImg.src = '';
                return;
            }
            if (!file.type.startsWith('image/')) {
                setError('gambar', 'File harus berupa gambar.');
                preview.hidden = true;
                previewImg.src = '';
                return;
            }
            setError('gambar', '');
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
                preview.hidden = false;
            };
            reader.readAsDataURL(file);
        });
    }
})();
// ✅ IIFE kedua yang duplikat → DIHAPUS SELURUHNYA


// ==================== STATE ====================
let barangDraft      = JSON.parse(localStorage.getItem('barangDraft')) || [];
let barcodeGenerated = false;


// ==================== BARCODE ====================
function generateBarcode() {
    const prefix    = 'BRG';
    const timestamp = Date.now().toString().slice(-6);
    const random    = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    const kode      = `${prefix}${timestamp}${random}`;
    document.getElementById('kodeBarang').value = kode;
    generateBarcodeImage(kode);
    barcodeGenerated = true;
}

function generateBarcodeImage(kode) {
    const barcodeDiv = document.getElementById('barcodeDisplay');
    if (!barcodeDiv) return;
    barcodeDiv.style.display = 'block';
    document.getElementById('barcode').innerHTML = '';
    JsBarcode('#barcode', kode, {
        format      : 'CODE128',
        width       : 2,
        height      : 50,
        displayValue: true,
        fontSize    : 16,
        background  : '#fff',
        lineColor   : '#000'
    });
    document.getElementById('barcodeText').textContent = `Kode: ${kode}`;
}


// ==================== PREVIEW GAMBAR ====================
function previewImage(event) {
    const input   = event.target;
    const preview = document.getElementById('imagePreview');
    if (!preview) return;

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.innerHTML = `
                <img src="${e.target.result}" class="preview-image" alt="Preview">
                <div class="mt-2">
                    <button type="button" class="btn btn-sm btn-outline-danger"
                            onclick="removeImage()">
                        <i class="fas fa-trash"></i> Hapus
                    </button>
                </div>`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function removeImage() {
    const gambarInput = document.getElementById('gambarBarang');
    if (gambarInput) gambarInput.value = '';

    const preview = document.getElementById('imagePreview');
    if (preview) {
        preview.innerHTML = `
            <i class="fas fa-image fa-3x text-muted mb-3"></i>
            <p class="text-muted">Belum ada gambar</p>
            <button type="button" class="btn btn-outline-primary scan-btn mt-2">
                <i class="fas fa-camera"></i> Pilih Gambar
                <input type="file" id="gambarBarang" accept="image/*"
                       onchange="previewImage(event)">
            </button>`;
    }
}


// ==================== SIMPAN KE SERVER ====================
async function simpanBarang(isDraft = false) {
    const formData = new FormData();
    const data = {
        kode        : document.getElementById('kodeBarang')?.value,
        nama        : document.getElementById('namaBarang')?.value,
        kategori    : document.getElementById('kategoriBarang')?.value,
        harga_beli  : document.getElementById('hargaBeli')?.value,
        harga_jual  : document.getElementById('hargaJual')?.value,
        stok        : document.getElementById('stokAwal')?.value,
        stok_minimum: document.getElementById('stokMinimum')?.value,
        satuan      : document.getElementById('satuanBarang')?.value,
        supplier    : document.getElementById('supplierBarang')?.value,
        deskripsi   : document.getElementById('deskripsiBarang')?.value,
        is_draft    : isDraft
    };

    const gambarInput = document.getElementById('gambarBarang');
    if (gambarInput?.files[0]) {
        formData.append('gambar', gambarInput.files[0]);
    }
    formData.append('data', JSON.stringify(data));

    try {
        const response = await fetch('/api/input-barang', { method: 'POST', body: formData });
        const result   = await response.json();

        if (result.success) {
            showSuccess(result.message);
            resetForm();
            loadRecentItems();
            if (!isDraft) removeFromDraft(data.kode);
        } else {
            showError(result.message || 'Gagal menyimpan barang');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Terjadi kesalahan pada server');
    }
}


// ==================== DRAFT ====================
function saveAsDraft() {
    if (!validateForm(true)) return;

    const draftData = {
        kode      : document.getElementById('kodeBarang')?.value  || `DRAFT_${Date.now()}`,
        nama      : document.getElementById('namaBarang')?.value,
        kategori  : document.getElementById('kategoriBarang')?.value,
        harga_beli: document.getElementById('hargaBeli')?.value,
        harga_jual: document.getElementById('hargaJual')?.value,
        stok      : document.getElementById('stokAwal')?.value,
        timestamp : new Date().toISOString()
    };

    barangDraft.push(draftData);
    localStorage.setItem('barangDraft', JSON.stringify(barangDraft));
    showSuccess('Berhasil disimpan sebagai draft!');
}

function removeFromDraft(kode) {
    barangDraft = barangDraft.filter(item => item.kode !== kode);
    localStorage.setItem('barangDraft', JSON.stringify(barangDraft));
}


// ==================== VALIDASI UTAMA ====================
function validateForm(isDraft = false) {
    if (isDraft) return true;

    const nama      = document.getElementById('namaBarang')?.value || '';
    const hargaJual = parseInt(document.getElementById('hargaJual')?.value?.replace(/\./g, '')) || 0;
    const hargaBeli = parseInt(document.getElementById('hargaBeli')?.value?.replace(/\./g, '')) || 0;
    const stok      = parseInt(document.getElementById('stokAwal')?.value) || 0;

    if (!nama.trim()) {
        showError('Nama barang harus diisi!');
        return false;
    }
    if (hargaJual <= 0) {
        showError('Harga jual harus lebih dari 0!');
        return false;
    }
    // ✅ Validasi harga jual > harga beli
    if (hargaJual <= hargaBeli) {
        showError('Harga jual harus lebih besar dari harga beli!');
        return false;
    }
    if (stok < 0) {
        showError('Stok tidak boleh negatif!');
        return false;
    }
    return true;
}


// ==================== RESET FORM ====================
function resetForm() {
    const formEl = document.getElementById('inputBarangForm');
    if (formEl) formEl.reset();
    removeImage();
    const barcodeDiv = document.getElementById('barcodeDisplay');
    if (barcodeDiv) barcodeDiv.style.display = 'none';
    barcodeGenerated = false;
}


// ==================== LOAD BARANG TERBARU ====================
async function loadRecentItems() {
    try {
        const response = await fetch('/api/barang-recent');
        const items    = await response.json();
        const tbody    = document.getElementById('recentItems')?.getElementsByTagName('tbody')[0];
        if (!tbody) return;

        tbody.innerHTML = '';
        items.forEach(item => {
            const row        = tbody.insertRow();
            const stockClass = item.stok <= item.stok_minimum
                ? 'stock-low'
                : item.stok <= item.stok_minimum * 2
                    ? 'stock-medium'
                    : 'stock-high';
            const stockText  = item.stok <= item.stok_minimum
                ? `${item.stok} (MIN!)`
                : item.stok;

            row.innerHTML = `
                <td><strong>${item.kode}</strong></td>
                <td>${item.nama}</td>
                <td><span class="badge bg-secondary">${item.kategori}</span></td>
                <td>
                    <span class="${stockClass} stock-indicator"></span>
                    ${stockText} ${item.satuan}
                </td>
                <td>Rp ${parseInt(item.harga_jual).toLocaleString('id-ID')}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary"
                            onclick="editItem('${item.kode}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-1"
                            onclick="deleteItem('${item.kode}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>`;
        });
    } catch (error) {
        console.error('Error loading recent items:', error);
    }
}


// ==================== EDIT & HAPUS ====================
async function editItem(kode) {
    try {
        const response = await fetch(`/api/barang/${kode}`);
        const item     = await response.json();

        document.getElementById('kodeBarang').value        = item.kode;
        document.getElementById('namaBarang').value        = item.nama;
        document.getElementById('kategoriBarang').value    = item.kategori;
        document.getElementById('hargaBeli').value         = item.harga_beli;
        document.getElementById('hargaJual').value         = item.harga_jual;
        document.getElementById('stokAwal').value          = item.stok;
        document.getElementById('stokMinimum').value       = item.stok_minimum;
        document.getElementById('satuanBarang').value      = item.satuan;
        document.getElementById('supplierBarang').value    = item.supplier  || '';
        document.getElementById('deskripsiBarang').value   = item.deskripsi || '';

        if (item.kode) generateBarcodeImage(item.kode);
        window.scrollTo(0, 0);

        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Update Barang';
            submitBtn.classList.replace('btn-primary', 'btn-warning');
        }
    } catch (error) {
        showError('Gagal memuat data barang');
    }
}

async function deleteItem(kode) {
    if (!confirm(`Apakah Anda yakin ingin menghapus barang ${kode}?`)) return;
    try {
        const response = await fetch(`/api/barang/${kode}`, { method: 'DELETE' });
        const result   = await response.json();
        if (result.success) {
            showSuccess('Barang berhasil dihapus!');
            loadRecentItems();
        } else {
            showError('Gagal menghapus barang');
        }
    } catch (error) {
        showError('Terjadi kesalahan saat menghapus');
    }
}


// ==================== NOTIFIKASI ====================
function showSuccess(message) {
    const el = document.getElementById('successMessage');
    if (el) el.textContent = message;
    const modal = new bootstrap.Modal(document.getElementById('successModal'));
    modal.show();
}

function showError(message) {
    alert('Error: ' + message);
}


// ==================== EVENT LISTENERS ====================
document.addEventListener('DOMContentLoaded', function () {
    loadRecentItems();

    const formEl = document.getElementById('inputBarangForm');
    if (formEl) {
        formEl.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!validateForm()) return;
            if (!barcodeGenerated) {
                if (!confirm('Barcode belum digenerate. Generate otomatis?')) return;
                generateBarcode();
            }
            simpanBarang(false);
        });
    }

    // Auto-generate kode dari nama barang
    const namaInput = document.getElementById('namaBarang');
    if (namaInput) {
        namaInput.addEventListener('blur', function () {
            const kodeInput = document.getElementById('kodeBarang');
            if (kodeInput && !kodeInput.value) {
                const nama = this.value.toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 10);
                if (nama.length >= 3) {
                    kodeInput.value = `BRG_${nama}_${Date.now().toString().slice(-4)}`;
                }
            }
        });
    }
});


// ==================== BARCODE SCANNER ====================
function startBarcodeScanner() {
    const barcode = prompt('Scan barcode atau masukkan kode secara manual:');
    if (barcode) {
        document.getElementById('kodeBarang').value = barcode;
        generateBarcodeImage(barcode);
        barcodeGenerated = true;
        checkExistingProduct(barcode);
    }
}

async function checkExistingProduct(kode) {
    try {
        const response = await fetch(`/api/check-barcode/${kode}`);
        const exists   = await response.json();
        if (exists) {
            if (confirm('Barang dengan kode ini sudah ada. Edit barang yang ada?')) {
                editItem(kode);
            }
        }
    } catch (error) {
        console.error('Error checking product:', error);
    }
}