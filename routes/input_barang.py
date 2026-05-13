import os
import io
import csv
import time
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
from models.db import db
from models.produk import Produk
from models import Stock
from routes.auth import login_required
# ✅ Hapus import generateBarcode yang tidak dipakai

input_barang_bp = Blueprint('input_barang', __name__, url_prefix='/input-barang')
import_barang_bp = Blueprint('import_barang', __name__, url_prefix='/import-barang')

UPLOAD_FOLDER    = 'static/uploads'
ALLOWED_EXTENSIONS = {'PNG', 'JPG', 'JPEG', 'GIF', 'BMP'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS


def bersihkan_angka(nilai_str):
    """Bersihkan format angka seperti 100.000 atau 100,000 sebelum konversi"""
    return nilai_str.replace('.', '').replace(',', '').strip()


# ─────────────────────────────────────────
# INPUT BARANG
# ─────────────────────────────────────────
@input_barang_bp.route('/', methods=['GET', 'POST'])
@login_required
def input_barang():
    if request.method == 'GET':
        daftar_produk = Produk.query.all()
        return render_template('input_barang.html', daftar_produk=daftar_produk)

    nama_barang = request.form.get('nama_barang', '').strip()
    kode_barang = request.form.get('kode_barang', '').strip()

    if not nama_barang or not kode_barang:
        flash('Pastikan semua field diisi dengan benar.', 'danger')
        return redirect(url_for('input_barang.input_barang'))

    try:
        # ✅ Bersihkan format angka sebelum konversi (penyebab bug di gambar)
        harga_beli = int(bersihkan_angka(request.form.get('harga_beli', '0')))
        harga_jual = int(bersihkan_angka(request.form.get('harga_jual', '0')))
        stok       = int(bersihkan_angka(request.form.get('stok', '0')))
        kategori   = request.form.get('kategori', '').strip()
    except ValueError:
        flash('Harga beli, harga jual, dan stok harus berupa angka.', 'danger')
        return redirect(url_for('input_barang.input_barang'))

    if harga_beli <= 0 or harga_jual <= 0:
        flash('Harga beli dan harga jual harus lebih dari 0.', 'danger')
        return redirect(url_for('input_barang.input_barang'))

    if stok < 0:
        flash('Stok tidak boleh negatif.', 'danger')
        return redirect(url_for('input_barang.input_barang'))

    # ✅ Perbaikan: <= bukan 
    if harga_jual <= harga_beli:
        flash('Harga jual harus lebih besar dari harga beli.', 'danger')
        return redirect(url_for('input_barang.input_barang'))

    # ✅ Perbaikan: pakai redirect agar daftar_produk tersedia
    if Produk.query.filter_by(kode_barang=kode_barang).first():
        flash('Kode barang sudah digunakan.', 'danger')
        return redirect(url_for('input_barang.input_barang'))

    # ── Upload gambar ──
    filename    = None
    gambar_file = request.files.get('gambar')
    if gambar_file and gambar_file.filename:
        if allowed_file(gambar_file.filename):
            name, ext = os.path.splitext(secure_filename(gambar_file.filename))
            filename  = f"{name}_{int(time.time())}{ext}"
            gambar_file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            flash('Format file tidak diizinkan. Gunakan: PNG, JPG, JPEG, GIF, BMP', 'danger')
            return redirect(url_for('input_barang.input_barang'))

    try:
        produk_baru = Produk(
            nama       = nama_barang,
            kode_barang= kode_barang,
            harga_beli = harga_beli,
            harga_jual = harga_jual,
            stok       = stok,
            gambar     = filename
        )
        db.session.add(produk_baru)
        db.session.flush()

        stock_baru = Stock(
            name            = nama_barang,
            quantity        = stok,
            kategori        = kategori,
            stok_rendah     = 10,
            total_produk    = stok,
            produk_tersedia = stok,
            price           = harga_jual
        )
        db.session.add(stock_baru)
        db.session.commit()

        flash('Data barang berhasil disimpan!', 'success')
        return redirect(url_for('input_barang.input_barang'))

    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyimpan data: ' + str(e), 'danger')
        return redirect(url_for('input_barang.input_barang'))


# ─────────────────────────────────────────
# INPUT BARANG JSON (API)
# ─────────────────────────────────────────
@input_barang_bp.route('/json', methods=['POST'])
@login_required
def input_barang_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Data tidak valid'}), 400

        nama_barang = data.get('nama_barang', '').strip()
        kode_barang = data.get('kode_barang', '').strip()
        kategori    = data.get('kategori', '').strip()

        if not nama_barang or not kode_barang:
            return jsonify({'success': False, 'message': 'Field wajib diisi'}), 400

        try:
            harga_beli = int(str(data.get('harga_beli', 0)).replace('.', ''))
            harga_jual = int(str(data.get('harga_jual', 0)).replace('.', ''))
            stok       = int(str(data.get('stok', 0)).replace('.', ''))
        except ValueError:
            return jsonify({'success': False, 'message': 'Harga dan stok harus angka'}), 400

        if harga_beli <= 0 or harga_jual <= 0:
            return jsonify({'success': False, 'message': 'Harga harus lebih dari 0'}), 400

        if stok < 0:
            return jsonify({'success': False, 'message': 'Stok tidak boleh negatif'}), 400

        # ✅ Perbaikan: <= bukan 
        if harga_jual <= harga_beli:
            return jsonify({'success': False, 'message': 'Harga jual harus lebih besar dari harga beli'}), 400

        if Produk.query.filter_by(kode_barang=kode_barang).first():
            return jsonify({'success': False, 'message': 'Kode barang sudah digunakan'}), 400

        produk_baru = Produk(
            nama       = nama_barang,
            kode_barang= kode_barang,
            harga_beli = harga_beli,
            harga_jual = harga_jual,
            stok       = stok
        )
        db.session.add(produk_baru)
        db.session.flush()

        stock_baru = Stock(
            name            = nama_barang,
            quantity        = stok,
            kategori        = kategori,
            stok_rendah     = 10,
            total_produk    = stok,
            produk_tersedia = stok,
            price           = harga_jual
        )
        db.session.add(stock_baru)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Data berhasil disimpan'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ─────────────────────────────────────────
# IMPORT BARANG (CSV)
# ─────────────────────────────────────────
@import_barang_bp.route('/', methods=['GET', 'POST'])
@login_required
def import_barang():
    if request.method == 'GET':
        return render_template('import_barang.html')

    try:
        file = request.files.get('file')
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'File tidak ditemukan'}), 400

        # ✅ Perbaikan: pakai csv.reader bukan iterasi mentah
        content = file.read().decode('utf-8-sig')  # utf-8-sig untuk handle BOM Excel
        reader  = csv.reader(io.StringIO(content))
        next(reader, None)  # skip header

        data = []
        for i, row in enumerate(reader, start=2):
            if len(row) < 5:
                return jsonify({
                    'success': False,
                    'message': f'Baris {i}: format tidak valid, butuh 5 kolom'
                }), 400
            try:
                data.append({
                    'nama_barang': row[0].strip(),
                    'kode_barang': row[1].strip(),
                    'harga_beli' : int(row[2].strip().replace('.', '')),
                    'harga_jual' : int(row[3].strip().replace('.', '')),
                    'stok'       : int(row[4].strip().replace('.', ''))
                })
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': f'Baris {i}: harga dan stok harus angka'
                }), 400

        for produk in data:
            if Produk.query.filter_by(kode_barang=produk['kode_barang']).first():
                return jsonify({
                    'success': False,
                    'message': f"Kode {produk['kode_barang']} sudah digunakan"
                }), 400

            db.session.add(Produk(
                nama       = produk['nama_barang'],
                kode_barang= produk['kode_barang'],
                harga_beli = produk['harga_beli'],
                harga_jual = produk['harga_jual'],
                stok       = produk['stok']
            ))
            db.session.add(Stock(
                name            = produk['nama_barang'],
                quantity        = produk['stok'],
                kategori        = '',
                stok_rendah     = 10,
                total_produk    = produk['stok'],
                produk_tersedia = produk['stok'],
                price           = produk['harga_jual']
            ))

        db.session.commit()
        return jsonify({'success': True, 'message': f'{len(data)} data berhasil diimport'})

    except ValueError:
        return jsonify({'success': False, 'message': 'Harga dan stok harus angka'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500