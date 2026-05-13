from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.kategori import Kategori
from models.base import db

kategori_bp = Blueprint('kategori', __name__, url_prefix='/kategori')


@kategori_bp.route('/')
def daftar_kategori():
    semua_kategori = Kategori.query.order_by(Kategori.nama).all()
    total_kategori = len(semua_kategori)
    total_produk = sum(kat.jumlah_produk for kat in semua_kategori)
    return render_template(
        'kategori.html',
        kategori=semua_kategori,
        total=total_kategori,
        total_produk=total_produk
    )


@kategori_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_kategori():
    if request.method == 'POST':
        nama = request.form.get('nama')
        deskripsi = request.form.get('deskripsi')
        icon = request.form.get('icon', '📦')
        warna = request.form.get('warna', '#4CAF50')

        if not nama:
            flash('Nama kategori wajib diisi!', 'error')
            return redirect(url_for('kategori.tambah_kategori'))

        if Kategori.query.filter_by(nama=nama).first():
            flash(f'Kategori "{nama}" sudah ada!', 'error')
            return redirect(url_for('kategori.tambah_kategori'))

        kategori_baru = Kategori(nama=nama, deskripsi=deskripsi, icon=icon, warna=warna)
        db.session.add(kategori_baru)
        db.session.commit()

        flash(f'Kategori "{nama}" berhasil ditambahkan!', 'success')
        return redirect(url_for('kategori.daftar_kategori'))

    return render_template('kategori/tambah.html')


# ========== EDIT KATEGORI (dengan validasi duplikat) ==========
@kategori_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_kategori(id):
    kategori = Kategori.query.get_or_404(id)

    if request.method == 'POST':
        nama_baru = request.form.get('nama', kategori.nama)

        # Cek duplikat nama (kecuali dirinya sendiri)
        existing = Kategori.query.filter(
            db.func.lower(Kategori.nama) == nama_baru.lower(),
            Kategori.id != id
        ).first()

        if existing:
            flash('Nama kategori sudah digunakan!', 'error')
            return redirect(url_for('kategori.edit_kategori', id=id))

        nama_lama = kategori.nama
        kategori.nama = nama_baru
        kategori.deskripsi = request.form.get('deskripsi', kategori.deskripsi)
        kategori.icon = request.form.get('icon', kategori.icon)
        kategori.warna = request.form.get('warna', kategori.warna)

        db.session.commit()
        flash(f'Kategori "{nama_lama}" berhasil diupdate!', 'success')
        return redirect(url_for('kategori.daftar_kategori'))

    return render_template('edit.html', kategori=kategori)


# ========== HAPUS KATEGORI ==========
@kategori_bp.route('/hapus/<int:id>', methods=['POST'])
def hapus_kategori(id):
    kategori = Kategori.query.get_or_404(id)
    nama_kategori = kategori.nama

    if kategori.jumlah_produk > 0:
        flash(f'Tidak bisa menghapus "{nama_kategori}" karena masih ada produk!', 'error')
        return redirect(url_for('kategori.daftar_kategori'))

    db.session.delete(kategori)
    db.session.commit()

    flash(f'Kategori "{nama_kategori}" berhasil dihapus!', 'success')
    return redirect(url_for('kategori.daftar_kategori'))


# ========== INIT DEFAULT KATEGORI ==========
@kategori_bp.route('/init-default')
def init_default():
    Kategori.create_default_categories()
    flash('Kategori default berhasil dibuat!', 'success')
    return redirect(url_for('kategori.daftar_kategori'))


# ========== API ==========
@kategori_bp.route('/api')
def api_kategori():
    kategori_list = Kategori.query.all()
    result = [
        {
            'id': kat.id,
            'nama': kat.nama,
            'icon': kat.icon,
            'warna': kat.warna,
            'jumlah_produk': kat.jumlah_produk
        }
        for kat in kategori_list
    ]
    return jsonify(result)


@kategori_bp.route('/api/<int:id>')
def api_kategori_detail(id):
    kategori = Kategori.query.get_or_404(id)
    return jsonify({
        'id': kategori.id,
        'nama': kategori.nama,
        'deskripsi': kategori.deskripsi,
        'icon': kategori.icon,
        'warna': kategori.warna,
        'created_at': kategori.created_at.isoformat() if kategori.created_at else None,
        'jumlah_produk': kategori.jumlah_produk
    })

def kategori_bp_routes(bp):
    bp.add_url_rule('/', view_func=daftar_kategori)
    bp.add_url_rule('/tambah', view_func=tambah_kategori, methods=['GET', 'POST'])
    bp.add_url_rule('/edit/<int:id>', view_func=edit_kategori, methods=['GET', 'POST'])
    bp.add_url_rule('/hapus/<int:id>', view_func=hapus_kategori, methods=['POST'])
    bp.add_url_rule('/init-default', view_func=init_default)
    bp.add_url_rule('/api', view_func=api_kategori)
    bp.add_url_rule('/api/<int:id>', view_func=api_kategori_detail)

def daftar_kategori():
    semua_kategori = Kategori.query.order_by(Kategori.nama).all()
    total_kategori = len(semua_kategori)
    total_produk = sum(kat.jumlah_produk for kat in semua_kategori)
    return render_template(
        'kategori.html',
        kategori=semua_kategori,
        total=total_kategori,
        total_produk=total_produk
    )

# ========== STATISTIK KATEGORI ==========
@kategori_bp.route('/statistik')
def statistik_kategori():
    kategori_list = Kategori.query.all()

    statistik = [
        {
            'nama': kat.nama,
            'icon': kat.icon,
            'warna': kat.warna,
            'jumlah_produk': kat.jumlah_produk,
            'persentase': 0
        }
        for kat in kategori_list
    ]

    total_produk = sum(item['jumlah_produk'] for item in statistik)

    for item in statistik:
        if total_produk > 0:
            item['persentase'] = round((item['jumlah_produk'] / total_produk) * 100, 1)

    return render_template(
        'kategori/statistik.html',
        statistik=statistik,
        total_produk=total_produk
    )