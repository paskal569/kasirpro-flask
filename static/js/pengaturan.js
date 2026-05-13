document.addEventListener('DOMContentLoaded', function () {
    loadPengaturan();
    loadFotoProfil(); // ✅ Dipanggil (sebelumnya didefinisikan tapi tidak dipanggil)

    // ── Event listener untuk semua input pengaturan ──────────────────────────
    document.querySelectorAll('.pengaturan-input').forEach(function (input) {
        input.addEventListener('change', function () {
            simpanPengaturan(this);
        });
    });

    // ── Tombol reset ──────────────────────────────────────────────────────────
    var tombolReset = document.getElementById('reset-pengaturan');
    if (tombolReset) {
        tombolReset.addEventListener('click', function () {
            resetPengaturan();
        });
    }

    // ── Tombol keamanan: toggle visibility password ───────────────────────────
    var tombolKeamanan = document.querySelector('.btn-security');
    if (tombolKeamanan) {
        tombolKeamanan.addEventListener('click', function (e) {
            e.preventDefault();
            var passwordInput = document.getElementById('password');
            var toggleIcon   = document.getElementById('toggle-password');
            if (!passwordInput || !toggleIcon) return;

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.classList.remove('fa-eye');
                toggleIcon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                toggleIcon.classList.remove('fa-eye-slash');
                toggleIcon.classList.add('fa-eye');
            }
        });
    }

    // ── Preview gambar profil saat dipilih ────────────────────────────────────
    // Sebelumnya: ada })(); tanpa pembuka IIFE → syntax error fatal
    // Sebelumnya: setError() dipanggil tapi tidak pernah didefinisikan
    var fileInput  = document.getElementById('gambar');
    var preview    = document.getElementById('gambar-preview');
    var previewImg = document.getElementById('gambar-preview-img');

    // Guard: hanya jalankan jika ketiga elemen ada di halaman
    if (fileInput && preview && previewImg) {
        fileInput.addEventListener('change', function () {
            var file = this.files && this.files[0];

            if (!file) {
                preview.hidden = true;
                previewImg.src = '';
                return;
            }

            if (!file.type.startsWith('image/')) {
                // setError() dihapus karena tidak terdefinisi
                // Diganti dengan tampilan pesan error sederhana
                alert('File harus berupa gambar.');
                preview.hidden = true;
                previewImg.src = '';
                return;
            }

            var reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
                preview.hidden = false;
            };
            reader.readAsDataURL(file);
        });
    }

    // ── Tampilkan nama user ───────────────────────────────────────────────────
    var elNamaUser = document.getElementById('nama-user');
    if (elNamaUser) {
        var nama = localStorage.getItem('nama');
        elNamaUser.textContent = nama ? nama : 'Pengguna';
    }
});

// ─── Load foto profil dari localStorage ──────────────────────────────────────
// Sebelumnya: fungsi ini didefinisikan tapi tidak pernah dipanggil
function loadFotoProfil() {
    var fotoData  = localStorage.getItem('profil_foto');
    var fotoProfil = document.getElementById('foto-profil');
    if (fotoData && fotoProfil) {
        fotoProfil.src = 'data:image/jpeg;base64,' + fotoData;
    }
}

// ─── Simpan nilai input ke localStorage ──────────────────────────────────────
function simpanPengaturan(elemen) {
    if (!elemen || !elemen.name) return;

    var key  = 'pengaturan_' + elemen.name;
    var nilai;

    if (elemen.type === 'checkbox') {
        nilai = elemen.checked ? '1' : '0';
    } else if (elemen.type === 'radio') {
        if (!elemen.checked) return;
        nilai = elemen.value;
    } else {
        nilai = elemen.value;
    }

    localStorage.setItem(key, nilai);
}

// ─── Muat nilai dari localStorage ke input ────────────────────────────────────
function loadPengaturan() {
    document.querySelectorAll('.pengaturan-input').forEach(function (input) {
        if (!input.name) return;

        var key   = 'pengaturan_' + input.name;
        var nilai = localStorage.getItem(key);
        if (nilai === null) return;

        if (input.type === 'checkbox') {
            input.checked = nilai === '1';
        } else if (input.type === 'radio') {
            input.checked = input.value === nilai;
        } else {
            input.value = nilai;
        }
    });
}

// ─── Reset semua pengaturan ke kondisi kosong ─────────────────────────────────
function resetPengaturan() {
    document.querySelectorAll('.pengaturan-input').forEach(function (input) {
        if (!input.name) return;

        localStorage.removeItem('pengaturan_' + input.name);

        if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = false;
        } else {
            input.value = '';
        }
    });
}

// ─── Sinkronisasi antar tab browser ──────────────────────────────────────────
window.addEventListener('storage', function (event) {
    if (event.key && event.key.startsWith('pengaturan_')) {
        loadPengaturan();
    }

    var elNamaUser = document.getElementById('nama-user');
    if (elNamaUser) {
        var nama = localStorage.getItem('nama');
        elNamaUser.textContent = nama ? nama : 'Pengguna';
    }
});

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Load data profil dari localStorage ke form ─────────────────────────
    loadProfilForm();

    // ── 2. Ubah Foto: klik tombol → trigger input file tersembunyi ────────────
    var tombolUbahFoto = document.querySelector('.btn-outline-peng');
    var inputFoto = document.getElementById('input-foto');

    if (tombolUbahFoto && inputFoto) {
        tombolUbahFoto.addEventListener('click', function (e) {
            e.preventDefault();
            inputFoto.click();
        });

        inputFoto.addEventListener('change', function () {
            var file = this.files && this.files[0];
            if (!file) return;

            if (!file.type.startsWith('image/')) {
                tampilkanPesan('danger', 'File harus berupa gambar (jpg, png, dll).');
                return;
            }

            var reader = new FileReader();
            reader.onload = function (e) {
                // Tampilkan foto di avatar
                var avatar = document.querySelector('.avatar');
                if (avatar) {
                    // Ganti teks "AD" dengan gambar
                    avatar.innerHTML = '<img src="' + e.target.result + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">';
                }
                // Simpan ke localStorage
                localStorage.setItem('profil_foto', e.target.result);
            };
            reader.readAsDataURL(file);
        });
    }

    // ── 3. Tombol Batal: reset form ke data localStorage ─────────────────────
    var tombolBatal = document.querySelector('.btn-cancel');
    if (tombolBatal) {
        tombolBatal.addEventListener('click', function (e) {
            e.preventDefault();
            loadProfilForm(); // Kembalikan isi form ke data tersimpan
        });
    }

    // ── 4. Tombol Simpan: validasi → simpan ke localStorage ──────────────────
    var tombolSimpan = document.querySelector('.btn-save');
    if (tombolSimpan) {
        tombolSimpan.addEventListener('click', function (e) {
            e.preventDefault();

            var namaLengkap = document.getElementById('nama-lengkap');
            var email       = document.getElementById('email');
            var telepon     = document.getElementById('telepon');

            // Validasi sederhana
            if (!namaLengkap.value.trim()) {
                tampilkanPesan('danger', 'Nama lengkap tidak boleh kosong.');
                namaLengkap.focus();
                return;
            }

            if (!email.value.trim() || !email.value.includes('@')) {
                tampilkanPesan('danger', 'Email tidak valid.');
                email.focus();
                return;
            }

            if (!telepon.value.trim()) {
                tampilkanPesan('danger', 'Nomor telepon tidak boleh kosong.');
                telepon.focus();
                return;
            }

            // Simpan ke localStorage
            localStorage.setItem('profil_nama',    namaLengkap.value.trim());
            localStorage.setItem('profil_email',   email.value.trim());
            localStorage.setItem('profil_telepon', telepon.value.trim());

            tampilkanPesan('success', 'Profil berhasil disimpan!');
        });
    }

    // ── 5. Tombol Ubah Password: redirect ke halaman keamanan ────────────────
    var tombolPassword = document.querySelector('.btn-security');
    if (tombolPassword) {
        tombolPassword.addEventListener('click', function (e) {
            e.preventDefault();
            // Arahkan ke halaman ganti password (sesuai route Flask)
            window.location.href = '/auth/change-password';
        });
    }

    // ── 6. Load foto profil dari localStorage ke avatar ──────────────────────
    loadFotoProfil();
});

// ─── Muat data profil dari localStorage ke dalam input form ──────────────────
function loadProfilForm() {
    var fields = {
        'nama-lengkap' : 'profil_nama',
        'email'        : 'profil_email',
        'telepon'      : 'profil_telepon'
    };

    Object.keys(fields).forEach(function (id) {
        var el    = document.getElementById(id);
        var nilai = localStorage.getItem(fields[id]);
        if (el && nilai) {
            el.value = nilai;
        }
    });
}

// ─── Load foto profil dari localStorage ke avatar ────────────────────────────
function loadFotoProfil() {
    var fotoData = localStorage.getItem('profil_foto');
    var avatar   = document.querySelector('.avatar');
    if (fotoData && avatar) {
        avatar.innerHTML = '<img src="' + fotoData + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">';
    }
}

// ─── Tampilkan pesan notifikasi (menggunakan Bootstrap alert) ─────────────────
function tampilkanPesan(tipe, pesan) {
    // Hapus alert sebelumnya jika ada
    var alertLama = document.getElementById('alert-profil');
    if (alertLama) alertLama.remove();

    var alert = document.createElement('div');
    alert.id = 'alert-profil';
    alert.className = 'alert alert-' + tipe + ' alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.cssText = 'z-index:99999;min-width:350px;border-radius:10px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.2);';
    alert.innerHTML = '<strong>' + pesan + '</strong>'
        + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';

    document.body.appendChild(alert);

    // Auto hilang setelah 3 detik
    setTimeout(function () {
        if (alert) alert.remove();
    }, 3000);
}