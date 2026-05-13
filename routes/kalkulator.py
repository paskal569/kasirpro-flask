from flask import Blueprint, render_template, request, jsonify
from models.pendapatan import Pendapatan
from models.db import db
from sqlalchemy import func, text
from datetime import datetime, date

kalkulator = Blueprint('kalkulator', __name__)

@kalkulator.route('/kalkulator', methods=['GET'])
def halaman_kalkulator():
    return render_template('kalkulator.html')

@kalkulator.route('/api/bayar', methods=['POST'])
def bayar():
    data         = request.get_json()
    nama_barang  = data.get('nama_barang', 'Tanpa Nama')
    total_harga  = float(data.get('total_harga', 0))
    jumlah_bayar = float(data.get('jumlah_bayar', 0))
    kembalian    = jumlah_bayar - total_harga

    if jumlah_bayar <= 0:
        return jsonify({'success': False, 'message': 'Jumlah bayar tidak valid'}), 400
    if jumlah_bayar < total_harga:
        return jsonify({'success': False, 'message': 'Pembayaran kurang dari total harga'}), 400

    try:
        baru = Pendapatan(
            nama_barang  = nama_barang,
            total_harga  = total_harga,
            jumlah_bayar = jumlah_bayar,
            kembalian    = kembalian,
            tanggal      = datetime.now()
        )
        db.session.add(baru)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

    return jsonify({'status': 'ok', 'kembalian': kembalian}), 200

@kalkulator.route('/api/stats', methods=['GET'])
def stats():
    today = date.today().strftime('%Y-%m-%d')
    try:
        rows = db.session.execute(text('''
            SELECT DATE(tanggal) as tgl, SUM(total_harga) as total_pendapatan
            FROM pendapatan
            GROUP BY DATE(tanggal)
            ORDER BY tgl DESC
        ''')).fetchall()

        stats_data = [{'tanggal': r[0], 'total_pendapatan': r[1]} for r in rows]

        omzet_hari_ini = next(
            (r[1] for r in rows if str(r[0]) == today), 0
        )

        transaksi_hari_ini = db.session.execute(text(
            'SELECT COUNT(*) as total FROM pendapatan WHERE DATE(tanggal) = :today'
        ), {'today': today}).fetchone()[0]

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    return jsonify({
        'stats': stats_data,
        'omzet_hari_ini': omzet_hari_ini,
        'transaksi_hari_ini': transaksi_hari_ini
    })