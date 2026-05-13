from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required
import datetime

# Inisialisasi Blueprint
pembayaran_selesai_bp = Blueprint(
    'pembayaran_selesai',
    __name__,
    url_prefix='/pembayaran_selesai'
)

@pembayaran_selesai_bp.route('/', methods=['GET'])
@login_required
def pembayaran_selesai():

    # Ambil data dari session
    status = session.get('pembayaran_selesai')  # ubah nama key biar jelas
    total = session.get('total_pembayaran')
    nama_user = session.get('nama_user')
    harga_total = session.get('harga_total')

    # Validasi utama (cukup satu pintu)
    if not status or not total or not nama_user or not harga_total:
        return redirect(url_for('pembayaran.pembayaran'))

    # Optional: ambil waktu sekarang
    waktu = datetime.datetime.now()

    return render_template(
        'pembayaran_selesai.html',
        total=total,
        nama_user=nama_user,
        harga_total=harga_total,
        waktu=waktu
    )