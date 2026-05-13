from flask import render_template, request, flash, redirect, url_for, Blueprint
from flask_login import login_required
from sqlalchemy import func
from datetime import date
from models.pelanggan import Pelanggan
from models.kunjungan import Kunjungan
from models.transaksi import transaksi as Transaksi
from models.item_transaksi import ItemTransaksi
from models.db import db

pelanggan_bp = Blueprint('pelanggan', __name__, url_prefix='/pelanggan')


def hitung_durasi_breakdown(start_date, end_date):
    breakdown = db.session.query(
        func.date_format(Kunjungan.jam_masuk, '%H:00').label('jam'),
        func.avg(Kunjungan.durasi_menit).label('durasi_rata_rata')
    ).filter(
        func.date(Kunjungan.jam_masuk) >= start_date,
        func.date(Kunjungan.jam_masuk) <= end_date
    ).group_by(func.date_format(Kunjungan.jam_masuk, '%H:00')).all()

    base = Kunjungan.query.filter(
        func.date(Kunjungan.jam_masuk) >= start_date,
        func.date(Kunjungan.jam_masuk) <= end_date,
    )

    return (
        {row.jam: f"{round(row.durasi_rata_rata)} menit" if row.durasi_rata_rata else "0 menit" for row in breakdown},
        {row.jam: round(row.durasi_rata_rata) if row.durasi_rata_rata else 0 for row in breakdown},
        {
            'cepat'  : base.filter(Kunjungan.durasi_menit <  5).count(),
            'singkat': base.filter(Kunjungan.durasi_menit.between(5, 14)).count(),
            'detail' : base.filter(Kunjungan.durasi_menit.between(15, 29)).count(),
            'lama'   : base.filter(Kunjungan.durasi_menit >= 30).count(),
        }
    )


@pelanggan_bp.route('/halaman_pelanggan', methods=['GET'])
def halaman_pelanggan():
    hari_ini = date.today()

    total_pengunjung = Kunjungan.query.filter(func.date(Kunjungan.jam_masuk) == hari_ini).count()

    total_pembelian = (
        Transaksi.query
        .filter(func.date(Transaksi.created_at) == hari_ini, Transaksi.status == 'selesai')
        .count()
    )

    total_penjualan = ItemTransaksi.query.filter(func.date(ItemTransaksi.created_at) == hari_ini).count()

    rata_durasi_row = db.session.query(func.avg(Kunjungan.durasi_menit)).filter(func.date(Kunjungan.jam_masuk) == hari_ini).scalar()
    rata_durasi = f"{round(rata_durasi_row or 0)} menit"

    conversion_rate_raw = db.session.query(func.avg(Kunjungan.total_belanja)).filter(func.date(Kunjungan.jam_masuk) == hari_ini).scalar()
    conversion_rate = f"Rp {round(conversion_rate_raw or 0):,}"

    pelanggan_list = Pelanggan.query.order_by(Pelanggan.created_at.desc()).all()

    rows = (
        db.session.query(
            func.date_format(Kunjungan.jam_masuk, '%H:00').label('jam'),
            func.count(Kunjungan.id).label('total'),
            func.sum(func.cast(Kunjungan.pembeli, db.Integer)).label('pembeli'),
            func.sum(Kunjungan.total_belanja).label('jumlah'),
        )
        .filter(func.date(Kunjungan.jam_masuk) == hari_ini)
        .group_by('jam').order_by('jam').all()
    )

    items = []
    for row in rows:
        pembeli       = row.pembeli or 0
        tidak_membeli = (row.total or 0) - pembeli
        conv          = f"{round(pembeli / row.total * 100)}%" if row.total else "0%"
        status        = "Ramai" if row.total >= 20 else ("Sedang" if row.total >= 10 else "Sepi")
        items.append({
            'jam': row.jam, 'total': row.total, 'pembeli': pembeli,
            'jumlah': row.jumlah or 0, 'tidak_membeli': tidak_membeli,
            'conversion_rate': conv, 'status': status,
        })

    # ✅ Unpack 3 nilai dari fungsi
    durasi_label, durasi_nilai, durasi_breakdown = hitung_durasi_breakdown(hari_ini, hari_ini)

    return render_template(
        'pelanggan.html',
        title            = 'Daftar Pelanggan',
        pelanggan_list   = pelanggan_list,
        items            = items,
        total_pengunjung = total_pengunjung,
        total_pembelian  = total_pembelian,
        total_penjualan  = total_penjualan,
        rata_durasi      = rata_durasi,
        conversion_rate  = conversion_rate,
        durasi_label     = durasi_label,
        durasi_nilai     = durasi_nilai,
        durasi_breakdown = durasi_breakdown,  # ✅ sekarang dict bukan tuple
        grafik_labels    = [i['jam']   for i in items],
        grafik_values    = [i['total'] for i in items],
        filter_aktif     = 'hari',
        hari_ini         = hari_ini,
    )

@pelanggan_bp.route('/detail/<string:nama_pelanggan>', methods=['GET'])
@login_required
def detail_pelanggan(nama_pelanggan):
    pelanggan = Pelanggan.query.filter_by(nama=nama_pelanggan).first_or_404(
        description=f"Pelanggan '{nama_pelanggan}' tidak ditemukan"
    )
    return render_template(
        'pelanggan/detail_pelanggan.html',
        title=f"Detail {nama_pelanggan}",
        pelanggan=pelanggan,
    )


@pelanggan_bp.route('/edit/<string:nama_pelanggan>', methods=['GET', 'POST'])
@login_required
def edit_pelanggan(nama_pelanggan):
    pelanggan = Pelanggan.query.filter_by(nama=nama_pelanggan).first_or_404()

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()

        if not nama:
            flash('Nama pelanggan tidak boleh kosong.', 'error')
            return render_template(
                'pelanggan/edit_pelanggan.html',
                title=f"Edit {nama_pelanggan}",
                pelanggan=pelanggan,
            )

        if nama != pelanggan.nama:
            sudah_ada = Pelanggan.query.filter_by(nama=nama).first()
            if sudah_ada:
                flash(f"Pelanggan dengan nama '{nama}' sudah ada.", 'error')
                return render_template(
                    'pelanggan/edit_pelanggan.html',
                    title=f"Edit {nama_pelanggan}",
                    pelanggan=pelanggan,
                )

        pelanggan.nama = nama
        db.session.commit()
        flash(f"Data pelanggan '{nama}' berhasil diperbarui.", 'success')
        return redirect(url_for('pelanggan.halaman_pelanggan'))

    return render_template(
        'pelanggan/edit_pelanggan.html',
        title=f"Edit {nama_pelanggan}",
        pelanggan=pelanggan,
    )


@pelanggan_bp.route('/grafik', methods=['GET'])
@login_required
def grafik():
    hari_ini = date.today()
    rows = (
        db.session.query(
            func.date_format(Kunjungan.jam_masuk, '%Y-%m').label('bulan'),
            func.sum(Kunjungan.total_belanja).label('total'),
        )
        .filter(func.date(Kunjungan.jam_masuk) >= hari_ini.replace(day=1))
        .group_by('bulan')
        .order_by('bulan')
        .all()
    )

    items = []
    for row in rows:
        items.append({
            'bulan': row.bulan,
            'total': row.total,
        })

    return render_template('pelanggan/grafik.html', items=items)