from flask import request, jsonify, Blueprint, render_template, redirect, url_for, flash
from models import Stock
from models.db import db

stock_bp = Blueprint('stock', __name__, url_prefix='/stock')
stock_product_bp = Blueprint('stock_product', __name__, url_prefix='/stock_product')


# ============ HALAMAN STOCK ============
@stock_bp.route('/')
def halaman_stock():
    # ✅ Filter search & kategori dari query string
    search = request.args.get('search', '').strip()
    kategori = request.args.get('kategori', '').strip()

    query = Stock.query
    if search:
        query = query.filter(Stock.name.ilike(f'%{search}%'))
    if kategori:
        query = query.filter(Stock.kategori == kategori)

    barang = query.all()
    semua_barang = Stock.query.all()

    total_produk   = len(semua_barang)
    stok_tersedia  = sum(1 for item in semua_barang if item.quantity > item.stok_rendah)
    stok_rendah    = sum(1 for item in semua_barang if 0 < item.quantity <= item.stok_rendah)
    stock_habis    = sum(1 for item in semua_barang if item.quantity == 0)
    kategoris      = sorted(set(item.kategori for item in semua_barang if item.kategori))

    return render_template(
        'stock.html',
        barang=barang,
        total_produk=total_produk,
        stok_tersedia=stok_tersedia,
        stok_rendah=stok_rendah,
        stock_habis=stock_habis,
        kategoris=kategoris
    )


# ============ EDIT STOK (modal form) ============
@stock_bp.route('/edit/<int:id>', methods=['POST'])  # ✅ POST bukan PUT
def edit_stock(id):
    stock = Stock.query.get_or_404(id)
    stok_baru = request.form.get('stok', type=int)

    if stok_baru is None or stok_baru < 0:
        flash('Jumlah stok tidak valid.', 'error')
        return redirect(url_for('stock.halaman_stock'))

    stock.quantity = stok_baru
    db.session.commit()
    flash(f'Stok "{stock.name}" berhasil diperbarui.', 'success')
    return redirect(url_for('stock.halaman_stock'))


# ============ HAPUS BARANG ============
@stock_bp.route('/delete/<int:id>', methods=['POST'])  # ✅ POST bukan DELETE
def delete_stock(id):
    stock = Stock.query.get_or_404(id)
    nama = stock.name
    db.session.delete(stock)
    db.session.commit()
    flash(f'Barang "{nama}" berhasil dihapus.', 'success')
    return redirect(url_for('stock.halaman_stock'))


# ============ API ROUTES (JSON) ============
@stock_bp.route('/list', methods=['GET'])
def get_stock_list():
    stock_list = Stock.query.all()
    data = [stock.to_dict() for stock in stock_list]
    return jsonify(data=data)

@stock_bp.route('/add', methods=['POST'])
def add_stock():
    data = request.get_json()
    stock = Stock(**data)
    db.session.add(stock)
    db.session.commit()
    return jsonify(message='Stock added successfully')


# ============ stock_product_bp ROUTES (API JSON) ============
@stock_product_bp.route('/list', methods=['GET'])
def get_stock_product_list():
    stock_list = Stock.query.all()
    data = [stock.to_dict() for stock in stock_list]
    return jsonify(data=data)

@stock_product_bp.route('/add', methods=['POST'])
def add_stock_product():
    data = request.get_json()
    stock = Stock(**data)
    db.session.add(stock)
    db.session.commit()
    return jsonify(message='Stock added successfully')

@stock_product_bp.route('/edit/<int:id>', methods=['POST'])  # ✅ POST bukan PUT
def edit_stock_product(id):
    stock = Stock.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(stock, key, value)
    db.session.commit()
    return jsonify(message='Stock edited successfully')

@stock_product_bp.route('/delete/<int:id>', methods=['POST'])  # ✅ POST bukan DELETE
def delete_stock_product(id):
    stock = Stock.query.get_or_404(id)
    db.session.delete(stock)
    db.session.commit()
    return jsonify(message='Stock deleted successfully')