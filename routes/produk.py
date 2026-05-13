from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.produk import Produk
from models.kategori import Kategori
from models.base import db
from routes.auth import login_required, admin_required
import json

produk_bp = Blueprint('produk', __name__, url_prefix='/produk')

@produk_bp.route('/')
@login_required
def produk():
    """Menampilkan semua produk"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter
    kategori_id = request.args.get('kategori', type=int)
    search = request.args.get('search', '')
    
    query = Produk.query.filter_by(is_active=True)
    
    if kategori_id:
        query = query.filter_by(kategori_id=kategori_id)
    
    if search:
        query = query.filter(Produk.nama.ilike(f'%{search}%'))
    
    # Sorting
    sort_by = request.args.get('sort', 'nama')
    if sort_by == 'stok':
        query = query.order_by(Produk.stok.asc())
    elif sort_by == 'harga':
        query = query.order_by(Produk.harga_jual.asc())
    else:
        query = query.order_by(Produk.nama.asc())
    
    produk_list = query.paginate(page=page, per_page=per_page, error_out=False)
    kategori_list = Kategori.query.filter_by(is_active=True).all()
   
    
    return render_template('produk.html', 
                         produk=produk_list,
                         kategori=kategori_list,
                         kategori_id=kategori_id,
                         search=search,
                         sort_by=sort_by)

@produk_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah():
    """Tambah produk baru"""
    if request.method == 'POST':
        try:
            # Generate kode otomatis jika tidak diisi
            kode = request.form.get('kode')
            if not kode:
                last_produk = Produk.query.order_by(Produk.id.desc()).first()
                if last_produk:
                    last_number = int(last_produk.kode.replace('P', ''))
                    new_number = last_number + 1
                else:
                    new_number = 1001
                kode = f'P{new_number:04d}'
            
            produk = Produk(
                kode=kode,
                nama=request.form.get('nama'),
                kategori_id=request.form.get('kategori_id'),
                harga_beli=float(request.form.get('harga_beli', 0)),
                harga_jual=float(request.form.get('harga_jual', 0)),
                stok=int(request.form.get('stok', 0)),
                stok_minimum=int(request.form.get('stok_minimum', 5)),
                satuan=request.form.get('satuan', 'pcs'),
                deskripsi=request.form.get('deskripsi'),
                barcode=request.form.get('barcode')
            )
            
            db.session.add(produk)
            db.session.commit()
            
            flash('Produk berhasil ditambahkan', 'success')
            return redirect(url_for('produk.detail', id=produk.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    kategori_list = Kategori.query.filter_by(is_active=True).all()
    return render_template('produk/tambah.html', kategori=kategori_list)

@produk_bp.route('/<int:id>')
@login_required
def detail(id):
    """Detail produk"""
    produk = Produk.query.get_or_404(id)
    return render_template('produk/detail.html', produk=produk)

@produk_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit produk"""
    produk = Produk.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            produk.nama = request.form.get('nama')
            produk.kategori_id = request.form.get('kategori_id')
            produk.harga_beli = float(request.form.get('harga_beli', 0))
            produk.harga_jual = float(request.form.get('harga_jual', 0))
            produk.stok = int(request.form.get('stok', 0))
            produk.stok_minimum = int(request.form.get('stok_minimum', 5))
            produk.satuan = request.form.get('satuan', 'pcs')
            produk.deskripsi = request.form.get('deskripsi')
            produk.barcode = request.form.get('barcode')
            
            db.session.commit()
            flash('Produk berhasil diupdate', 'success')
            return redirect(url_for('produk.detail', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    kategori_list = Kategori.query.filter_by(is_active=True).all()
    return render_template('produk/edit.html', produk=produk, kategori=kategori_list)

@produk_bp.route('/<int:id>/hapus', methods=['POST'])
@login_required
@admin_required
def hapus(id):
    """Hapus produk (soft delete)"""
    produk = Produk.query.get_or_404(id)
    produk.is_active = False
    db.session.commit()
    
    flash('Produk berhasil dihapus', 'success')
    return redirect(url_for('produk.index'))

@produk_bp.route('/api/cari')
@login_required
def api_cari():
    """API untuk pencarian produk cepat"""
    keyword = request.args.get('q', '')
    
    if keyword:
        produk_list = Produk.query.filter(Produk.nama.ilike(f'%{keyword}%')).limit(10).all()  # Batasi 10 hasil
    else:
        produk_list = Produk.query.filter_by(is_active=True).limit(10).all()
    
    result = []
    for p in produk_list:
        result.append({
            'id': p.id,
            'kode': p.kode,
            'nama': p.nama,
            'harga_jual': p.harga_jual,
            'stok': p.stok,
            'satuan': p.satuan
        })
    
    return jsonify(result)

@produk_bp.route('/api/<int:id>')
@login_required
def api_detail(id):
    """API untuk mendapatkan detail produk"""
    produk = Produk.query.get_or_404(id)
    
    return jsonify({
        'id': produk.id,
        'kode': produk.kode,
        'nama': produk.nama,
        'harga_jual': produk.harga_jual,
        'harga_beli': produk.harga_beli,
        'stok': produk.stok,
        'satuan': produk.satuan,
        'kategori': produk.kategori.nama if produk.kategori else '',
        'margin': produk.margin,
        'keuntungan': produk.keuntungan
    })

@produk_bp.route('/stok-menipis')
@login_required
def stok_menipis():
    """Produk dengan stok menipis"""
    produk_list = Produk.stok_menipis()
    return render_template('produk/stok_menipis.html', produk=produk_list)

@produk_bp.route('/<int:id>/tambah-stok', methods=['POST'])
@login_required
@admin_required
def tambah_stok(id):
    """Tambah stok produk"""
    produk = Produk.query.get_or_404(id)
    jumlah = int(request.form.get('jumlah', 0))
    
    if jumlah > 0:
        produk.tambah_stok(jumlah)
        flash(f'Stok berhasil ditambah {jumlah} {produk.satuan}', 'success')
    
    return redirect(url_for('produk.detail', id=id))