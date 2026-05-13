// --- BAGIAN BACKUP ---
document.getElementById('backup-btn').addEventListener('click', function() {
    const btn = this;
    btn.disabled = true; // Cegah double click

    fetch('/backup')
        .then(response => {
            if (!response.ok) throw new Error('Gagal mengunduh backup');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `backup-${new Date().toISOString().slice(0,10)}.sql`; // Nama file lebih informatif
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(err => alert('Error: ' + err.message))
        .finally(() => btn.disabled = false);
});

// --- BAGIAN RESTORE ---
const restoreInput = document.getElementById('restore-input');
const restoreBtn = document.getElementById('restore-btn');

// Klik tombol restore akan memicu pemilihan file
restoreBtn.addEventListener('click', () => restoreInput.click());

// Begitu file dipilih, otomatis upload
restoreInput.addEventListener('change', function() {
    if (this.files.length === 0) return;

    const formData = new FormData();
    formData.append('file', this.files[0]);

    // Beri feedback visual sederhana
    restoreBtn.textContent = 'Uploading...';
    restoreBtn.disabled = true;

    fetch('/restore', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        alert('Status: ' + result);
        // Refresh halaman jika diperlukan agar data baru muncul
        // location.reload();
    })
    .catch(err => alert('Upload gagal: ' + err.message))
    .finally(() => {
        restoreBtn.textContent = 'Restore Backup';
        restoreBtn.disabled = false;
        this.value = ''; // Reset input file
    });
});



